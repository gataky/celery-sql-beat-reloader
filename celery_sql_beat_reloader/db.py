from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import NullPool


class Manager(object):
    def __init__(self, dburl):
        self._engine = create_engine(dburl, poolclass=NullPool)
        self._session = None

    @property
    def session(self):
        if self._session:
            return self._session
        self._session = Session(self._engine)
        return self._session

    def close(self):
        self._engine.dispose()

    @property
    @contextmanager
    def cleanup(self):
        try:
            yield
            self._session.commit()
        except Exception as err:
            self._session.rollback()
            raise err
        finally:
            self._session.close()
            self._session = None
