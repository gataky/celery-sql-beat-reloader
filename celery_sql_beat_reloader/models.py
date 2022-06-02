from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

from celery_sql_beat_reloader.crontabtz import crontabtz

"""

CREATE TABLE celery_beat_schedule (
    id SERIAL PRIMARY KEY,
    created_date TIMESTAMPTZ DEFAULT NOW(),
    updated_date TIMESTAMPTZ DEFAULT NOW(),
    last_scheduled_date TIMESTAMPTZ,
    active BOOLEAN DEFAULT TRUE,

    name TEXT NOT NULL UNIQUE,
    task TEXT NOT NULL,

    args   JSONB DEFAULT '[]',
    kwargs JSONB DEFAULT '{}',

    type          TEXT NOT NULL DEFAULT 'cron',
    seconds       INTEGER DEFAULT 60,
    minute        TEXT DEFAULT '*',
    hour          TEXT DEFAULT '*',
    day_of_week   TEXT DEFAULT '*',
    day_of_month  TEXT DEFAULT '*',
    month_of_year TEXT DEFAULT '*',
    timezone      TEXT DEFAULT 'America/Los_Angeles'
);
COMMENT ON COLUMN celery_beat_schedule.task    IS 'the import path of the task e.g. solv.celery.scheduled.foo.task';
COMMENT ON COLUMN celery_beat_schedule.args    IS 'args will be unpacked as *args when executing the task';
COMMENT ON COLUMN celery_beat_schedule.kwargs  IS 'kwargs will be unpacked as **kwargs when executing the task';
COMMENT ON COLUMN celery_beat_schedule.type    IS 'type is either cron or periodic';
COMMENT ON COLUMN celery_beat_schedule.seconds IS 'if type is periodic then the seconds column will be used for schedule';

"""


class Beat(declarative_base()):
    __tablename__ = "celery_beat_schedule"
    TYPE_CRON = "cron"
    TYPE_PERIODIC = "periodic"

    id = sa.Column(sa.Integer(), primary_key=True, autoincrement=True)

    created_date = sa.Column(sa.DateTime(timezone=True), default=datetime.utcnow)
    updated_date = sa.Column(sa.DateTime(timezone=True), default=datetime.utcnow)
    last_scheduled_date = sa.Column(sa.DateTime(timezone=True))

    active = sa.Column(sa.Boolean(), default=True)

    name = sa.Column(sa.Text(), nullable=False, unique=True)
    task = sa.Column(sa.Text(), nullable=False)

    args = sa.Column(JSONB, default=[])
    kwargs = sa.Column(JSONB, default={})

    type = sa.Column(sa.Text(), default=TYPE_CRON)

    seconds = sa.Column(sa.Integer(), default=60)
    minute = sa.Column(sa.Text(), default="*")
    hour = sa.Column(sa.Text(), default="*")
    day_of_week = sa.Column(sa.Text(), default="*")
    day_of_month = sa.Column(sa.Text(), default="*")
    month_of_year = sa.Column(sa.Text(), default="*")
    timezone = sa.Column(sa.Text(), default="*")

    @property
    def schedule(self):
        if self.type == Beat.TYPE_CRON:
            schedule = crontabtz(**{f: getattr(self, f) for f in crontabtz.FIELDS})
        else:
            schedule = self.seconds
        return {
            self.name: {
                "task": self.task,
                "schedule": schedule,
                "args": self.args,
                "kwargs": self.kwargs,
            }
        }
