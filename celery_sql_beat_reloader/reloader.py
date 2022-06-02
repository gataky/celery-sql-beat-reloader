import time
from datetime import datetime

import pytz
from celery.beat import Scheduler
from celery.utils.log import get_logger

from celery_sql_beat_reloader import db, models

logger = get_logger(__name__)
debug, info, error = (logger.debug, logger.info, logger.error)


class Reloader(Scheduler):
    def __init__(self, *args, app=None, **kwargs):
        self._store = {}
        dburl = kwargs.get("dburl") or app.conf.get("beat_reloader_dburl")
        self.db = db.Manager(dburl)
        super().__init__(*args, app=app, **kwargs)

    @property
    def schedule(self):
        return self._store

    @schedule.setter
    def schedule(self, beat):
        self._store.update(beat)

    def setup_schedule(self):
        self.sync()

    def sync(self):
        with self.db.cleanup:
            beats = self.db.session.query(models.Beat).filter_by(active=True).all()
            new_beats = {}
            for beat in beats:
                new_beats.update(beat.schedule)
            self.merge_inplace(new_beats)
            self.populate_heap()
            self.display_schedule()

    def display_schedule(self):
        entries = sorted(self.schedule.values(), key=lambda e: e.name)
        info(
            f"Current schedule, {len(entries)} entries:\n\t"
            + "\n\t".join(repr(entry) for entry in entries)
        )

    def apply_entry(self, entry, producer=None):
        super().apply_entry(entry, producer=producer)
        with self.db.cleanup:
            beat = self.db.session.query(models.Beat).filter_by(name=entry.name).first()
            when = datetime.now(tz=pytz.timezone(beat.timezone))
            beat.last_scheduled_date = when

    def should_sync(self):
        return (
            self._last_sync is None
            or time.monotonic() - self._last_sync > self.max_interval
        )

    def close(self):
        self.db.close()
