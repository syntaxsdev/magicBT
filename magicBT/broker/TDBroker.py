from magicBT.broker.base import DataBroker
from magicBT.models.series import IndicatorData, TimeSeries
from .QueueService import SafeQueueService

from twelvedata import TDClient
from typing import Union, Optional
from datetime import datetime
import threading


class TDBroker(DataBroker):
    def __init__(self, api_key: str, credits: int):
        super().__init__()
        self.TDC: TDClient = TDClient(apikey=api_key)
        self.max_output_size = 5000
        self.timezone = "America/New_York"
        self.SQS = SafeQueueService(credits)

    def get(self, stock: str, interval: str, indicators: Optional[list[IndicatorData]] = None, **kwargs):
        ts_build = self.TDC.time_series(
            symbol=stock,
            interval=interval,
            outputsize=self.max_output_size,
            timezone=self.timezone,
            **kwargs
        )
        
        if indicators:
            for i in indicators:
                if i.indicator == "sma":
                    ts_build = ts_build.with_ma(**i.data)
                elif i.indicator == "ema":
                    ts_build = ts_build.with_ema(**i.data)
                elif i.indicator == "bb":
                    ts_build = ts_build.with_bbands(**i.data)
                elif i.indicator == "vwap":
                    ts_build = ts_build.with_vwap(**i.data)

        return self.SQS.queue(
            timeseries=ts_build,
            format="json"
        )
    
    def gather_backtest(self, stock: str, start_time: Union[datetime, str], 
                        interval: str, indicators: Optional[Union[str, list[IndicatorData]]] = None) -> TimeSeries:
        
        if indicators and isinstance(indicators, str):
            indicators = [indicators]

        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%Y/%m/%d")
            iso_format = start_time.isoformat()

        end_dates = super().generate_end_dates(
            start_date=start_time,
            interval=interval,
            max_output=self.max_output_size
        )

        TS = TimeSeries()
        """
        TWELVEDATA MODULE DOES NOT SUPPORT ASYNC HTTP (AIOHTTP). WHEN IT DOES, WILL USE THIS SNIPPET #TODO
        tasks = []
        for date in end_dates:
            task = asyncio.ensure_future(self.get(stock=stock, interval=interval, end_date=date, indicators=indicators))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        write_log = [TS.extend(result) for result in results]
        """
        threads = []
        results = []
        for date in end_dates:
            thread = threading.Thread(
                target=lambda: results.append(self.get(stock=stock, 
                    interval=interval, 
                    end_date=date, 
                    indicators=indicators))
                )
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        for result in results:
            TS.extend(result)
        TS.sort()
        TS.chop_to_date(iso_format)
        """
        write_log = [TS.extend(self.get(stock=stock, 
                    interval=interval, 
                    end_date=date,
                    indicators=indicators)) for date in end_dates]
        """
        return TS
    
    