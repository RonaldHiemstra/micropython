import ntptime  #pylint: disable=import-error
from machine import RTC  #pylint: disable=import-error
import time


class localtime():
    """Synchronized realtime clock using NTP."""
    def __init__(self, utcOffset):
        self.utcOffset = utcOffset
        self.__synced = None
        self._sync()

    def _sync(self):
        ntptime.settime()   # Synchronize the system time using NTP
        # year, month, day, week_of_year, hour, minute, second, millisecond
        # TODO: or is it: year, month, day, day_of_week, hour, minute, second, millisecond
        datetime_ymd_w_hms_m = list(RTC().datetime())
        datetime_ymd_w_hms_m[4] += self.utcOffset
        RTC().init(datetime_ymd_w_hms_m)
        self.__synced = datetime_ymd_w_hms_m[2]
        del datetime_ymd_w_hms_m

    def now(self):
        """Retrieve the current time in milliseconds accurate."""
        class now():
            def __init__(self):
                (self.year, self.month, self.day, self.dow,
                 self.hour, self.minute, self.second, self.millisecond) = RTC().datetime()
        dt = now()
        if dt.day != self.__synced and dt.hour == 4:  # sync every day @ 4am
            self._sync()
            dt = now()
        return dt

#dt = localtime(1)
