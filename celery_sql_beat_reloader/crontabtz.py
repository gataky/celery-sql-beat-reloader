import pytz
from celery.schedules import crontab


class crontabtz(crontab):

    FIELDS = (
        "minute",
        "hour",
        "day_of_week",
        "day_of_month",
        "month_of_year",
        "timezone",
    )

    REPR = (
        "<crontab: "
        + "{0._orig_minute} "
        + "{0._orig_hour} "
        + "{0._orig_day_of_week} "
        + "{0._orig_day_of_month} "
        + "{0._orig_month_of_year} "
        + "(m/h/d/dM/MY) {0.tz}>"
    )

    def __init__(self, *args, timezone="utc", **kwargs):
        self.tz = timezone
        super().__init__(*args, **kwargs)

    def maybe_make_aware(self, dt):
        return dt.astimezone(pytz.timezone(self.tz))

    def __repr__(self):
        return crontabtz.REPR.format(self)
