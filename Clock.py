from datetime import datetime, timedelta
from collections import namedtuple
import json
from json.decoder import JSONDecodeError

Alarm = namedtuple("Alarm", "day_of_week, hour minute enabled duration_minutes")


class Clock:
    current_time = datetime.now()
    alarm: Alarm
    alarm_in_progress:Alarm = None

    def __init__(self) -> None:
        self.alarm = Clock._load_alarm()

    def save_alarm(self):
        serialized_alarm = json.dumps(self.alarm._asdict())
        with open("alarm.json", "w") as f:
            f.write(serialized_alarm)

    @staticmethod
    def _load_alarm():
        try:
            with open("alarm.json", "r") as f:
                serialized_alarm = f.read()
                return Alarm(**json.loads(serialized_alarm))
        except FileNotFoundError or TypeError or JSONDecodeError:
            return Alarm(hour=0, minute=0, day_of_week=[], enabled=False, duration_minutes=0)


clock = Clock()


def update():
    clock.current_time = datetime.now()


def get_time():
    return clock.current_time.strftime("%H:%M:%S")


def maybe_trigger_alarm():
    if clock.alarm_in_progress or not clock.alarm or not clock.alarm.enabled:
        return False
    if not clock.current_time.weekday() in clock.alarm.day_of_week:
        return False
    alarm_trigger_start = clock.current_time.replace(hour=clock.alarm.hour, minute=clock.alarm.minute, second=0, microsecond=0)
    alarm_trigger_end = alarm_trigger_start + timedelta(seconds=1)
    if alarm_trigger_start <= clock.current_time <= alarm_trigger_end:
        clock.alarm_in_progress = clock.alarm
        return True


def alarm_is_on() -> bool:
    return clock.alarm_in_progress


def maybe_stop_alarm():
    if not clock.alarm_in_progress:
        return False
    alarm_start = clock.current_time.replace(hour=clock.alarm.hour, minute=clock.alarm.minute, second=0, microsecond=0)
    alarm_end = alarm_start + timedelta(minutes=clock.alarm_in_progress.duration_minutes)
    if clock.current_time > alarm_end:
        clock.alarm_in_progress = None
        return True


def stop_alarm():
    if not clock.alarm_in_progress:
        return False
    clock.alarm_in_progress = None
    return True


def set_alarm(alarm: Alarm):
    clock.alarm = alarm
    clock.save_alarm()


def get_alarm():
    return clock.alarm


def on_beat():
    return clock.current_time.second % 2 == 0


def get_days_str(ordinals):
    if ordinals == [0, 1, 2, 3, 4, 5, 6]:
        return 'All Days'
    if ordinals == [0, 1, 2, 3, 4]:
        return 'Weekdays'
    if ordinals == [5, 6]:
        return 'Weekend'
    return ','.join([['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su'][i] for i in ordinals])
