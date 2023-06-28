from typing import Optional, Union
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class DataBroker(ABC):
    MARKET_START_TIME = timedelta(hours=9, minutes=30)
    MARKET_END_TIME = timedelta(hours=16, minutes=0)
    MARKET_DAYS = set([0, 1, 2, 3, 4])

    def __init__(self):
        self.smm = 390
        self.intervals: dict[str, int] = {
            '1min': 1,
            '5min': 5,
            '10min': 10,
            '15min': 15,
            '30min': 30,
            '1hr': 60,
            '2hr': 180,
            '4hr': 360,
            '1d': 390
        }
        ...

    @abstractmethod
    def gather_backtest(self):
        ...
    
    def generate_end_dates(self, start_date: Union[datetime, str], interval: Union[str, int], max_output: int):
        if type(interval) == str:
            interval = self.interval_to_int(interval)

        if type(start_date) == str:
            start_date = datetime.strptime(start_date, "%Y/%m/%d")
        
        end_dates = []
        current_datetime = start_date

        # Calculate number of intervals per day
        intervals_per_day = 390 // interval

        # Calculate how many days are needed to reach max_output
        days_needed = max_output // intervals_per_day

        # If max_output is less than intervals_per_day, set days_needed to 1
        if days_needed == 0:
            days_needed = 1

        # Count to keep track of the added days
        day_count = 0

        while current_datetime < datetime.now():
            # Check if current day is a market day
            if current_datetime.weekday() in self.MARKET_DAYS:
                day_count += 1
                # Only add the date to end_dates when we reach a multiple of days_needed
                if day_count == days_needed:
                    end_dates.append(current_datetime)
                    day_count = 0  # Reset the day_count

            # Move to the next day
            current_datetime += timedelta(days=1)

        # Add the last date if it's a market day and we've processed at least one block of time
        if current_datetime.weekday() in self.MARKET_DAYS and day_count > 0:
            end_dates.append(current_datetime)

        return end_dates



    
    def interval_to_int(self, interval: str) -> int:
        return self.intervals[interval]
    