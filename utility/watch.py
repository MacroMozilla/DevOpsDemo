import functools
import datetime
import time


class Watch:
    """A simple stopwatch class using the datetime library."""
    def __init__(self, fctn=datetime.datetime.now):
        self.fctn = fctn
        self.tick = self.fctn()
        self.records = []

    def see_timedelta(self):
        """Records and returns the timedelta since the last check."""
        tick = self.fctn()
        res = tick - self.tick
        self.records.append(res)
        self.tick = tick
        return res

    def see_seconds(self):
        """Records and returns the seconds since the last check."""
        return round(self.see_timedelta().total_seconds(), 6)

    def total_timedelta(self):
        """Returns the total accumulated timedelta from all records."""
        # Use datetime.timedelta() as the starting value for the sum
        totalTime = sum(self.records, datetime.timedelta())
        return totalTime

    def total_seconds(self):
        """Returns the total accumulated seconds from all records."""
        return round(self.total_timedelta().total_seconds(), 6)


def watch_time(func):
    """A decorator to measure and print the execution time of a function."""
    @functools.wraps(func)
    def wrap(*args, **kwargs):
        w = Watch()
        res = func(*args, **kwargs)

        # The first and only call to see_seconds() measures the total duration
        print(f"Time Cost : '{func.__name__}' took {w.see_seconds()} seconds")
        return res

    return wrap


if __name__ == '__main__':
    # ======================================================================
    # Demo 1: Using the @watch_time decorator
    # This is the most common and simplest usage, automatically measuring
    # the execution time of the entire function.
    # ======================================================================
    print("--- Demo 1: @watch_time Decorator ---")


    @watch_time
    def decorated_function(sleep_duration):
        """An example decorated function that will sleep for a period of time."""
        print(f"Function 'decorated_function' is running, it will sleep for {sleep_duration} seconds...")
        time.sleep(sleep_duration)
        return "Decorator test completed!"


    result = decorated_function(1.2)
    print(f"Function return value: {result}\n")

    # ======================================================================
    # Demo 2: Manually using all methods of the Watch class
    # This demo will call each method of the Watch class step by step
    # to show its specific functionality.
    # ======================================================================
    print("--- Demo 2: Manually testing each method of the Watch class ---")

    # 1. __init__: Create a Watch instance, the internal timer starts.
    print("1. Creating Watch instance...")
    manual_watch = Watch()
    time.sleep(0.5)  # Simulate the first time period

    # 2. see_timedelta: View the timedelta object from the last record to now.
    # This is the first call, so it measures the time from __init__ to now.
    td1 = manual_watch.see_timedelta()
    print(f"2. Called see_timedelta() -> Recorded the first time period: {td1} (type: {type(td1)})")

    time.sleep(0.7)  # Simulate the second time period

    # 3. see_seconds: View the number of seconds (float) since the last record.
    # This records the second time period and returns it in seconds.
    secs2 = manual_watch.see_seconds()
    print(f"3. Called see_seconds() -> Recorded the second time period: {secs2} seconds (type: {type(secs2)})")

    # `manual_watch.records` now contains two timedelta objects
    print(f"   The internal record list `records` now contains {len(manual_watch.records)} timedelta objects.")

    # 4. total_timedelta: Calculate and return the sum of all recorded periods (timedelta object).
    total_td = manual_watch.total_timedelta()
    print(f"4. Called total_timedelta() -> Total recorded time: {total_td} (type: {type(total_td)})")

    # 5. total_seconds: Calculate and return the total recorded time in seconds (float).
    total_secs = manual_watch.total_seconds()
    print(f"5. Called total_seconds() -> Total recorded seconds: {total_secs} seconds (type: {type(total_secs)})")

    # Verification
    # Note: Since code execution itself takes a tiny bit of time,
    # the direct addition result may slightly differ from the total.
    print(f"\nVerification: First period seconds ({td1.total_seconds():.6f}) + Second period seconds ({secs2:.6f}) = {td1.total_seconds() + secs2:.6f}")
    print(f"This result should be approximately equal to total_seconds() result ({total_secs:.6f}).")
