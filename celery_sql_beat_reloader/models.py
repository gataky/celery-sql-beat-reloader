from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

from celery_sql_beat_reloader.crontabtz import crontabtz


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
