from twelvedata import TDClient
from twelvedata.time_series import TimeSeries
from datetime import datetime as dt
import time

"""
This service class will eventually be redone, I've reused it for some time.
I coded this over a year ago (late 2021) and it's very bulky. Can be improved and has been noted.

"""
class SafeQueueService:
    """
    Keeps track of the queue and removes queues items after 60 seconds (safe aspect)
    rather than more dynamically
    """

    creditsPM: int = None
    remaining: int = 0
    minuteStarted: int = 0
    _queue: dict = {}
    busy: bool = False

    def __init__(self, credits):
        self.creditsPM = credits
        self.remaining = credits


    def queue(self, timeseries: TimeSeries, format: str):
        credits = len(timeseries.as_url()) if type(timeseries.as_url()) is list else 1
        print("Queuing {0} credits".format(credits))
        
        if (self.remaining - credits) < 0:
            self.busy = True
            print("The queue is full. Retrying...")
            while (self.remaining - credits) < 0:
                self.QueueRefresh()
                time.sleep(2)
                if (self.remaining - credits) >= 0:
                    self.busy = False
                    print("The queue is open.")
                    break

        # Proceed with queueing
        currTime = self._unixunique()
        self._queue[currTime] = credits
        self.remaining -= credits
        retval = None
        if format == "pandas":
            retval = timeseries.as_pandas()
        elif format == "json":
            retval = timeseries.as_json()
        elif format == "plotly":
            retval = timeseries.as_plotly_figure()
        return retval


    def _credit_check(self):
        self.remaining = self.remaining if self.remaining < self.creditsPM else self.creditsPM


    def QueueRefresh(self):
        queue = self._queue.copy()

        for q in queue:
            currTime = self._unixunique()

            #If the queue has been there for 60 seconds remove it
            if (currTime - q) >= 60:
                credits = self._queue.pop(q)
                self.remaining += credits

        return self.remaining


    def _unixunique(self):
        return time.time()

    def _unix(self):
        ms = dt.now()
        return int(time.mktime(ms.timetuple()))
