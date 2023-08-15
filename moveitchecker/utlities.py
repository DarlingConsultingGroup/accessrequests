import json
from datetime import datetime, timedelta
import pandas as pd
from zoneinfo import ZoneInfo



def currentEasternTimestampString(lookbackMinutes=0):
    eastern_time = datetime.now(ZoneInfo("America/New_York"))
    lookback_timestamp = eastern_time - timedelta(minutes=lookbackMinutes)
    timestamp_str = lookback_timestamp.strftime("%Y-%m-%d %H:%M:%S")
    return timestamp_str




