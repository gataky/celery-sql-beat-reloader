# IN DEVELOPMENT

# celery-sql-beat-reloader

A celery schedule that will sync with a db for the latest schedule of tasks.

## Features

- Pulls schedule from a database instead of code.
- Every schedule is timezone aware.


## Getting Started

### Prerequisites

- Python 3
- celery >= 5.2
- sqlalchemy

### Installing

Install from PyPi:

```
$ pip install celery-sql-beat-reloader
```

Install from source by cloning this repository:

```
$ git clone git@github.com:sir-wiggles/celery-sql-beat-reloader.git
$ cd celery-sql-beat-reloader
$ python setup.py install
```

## Usage

`celery_sql_beat_reloader` uses sqlalchemy to manage database connections so you should in theory be able to use this on any flavor of SQL database.

### Schema

```sql
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
```

> NOTE: Table is not auto generated.

### Column Descriptions

* `active` - indicates if the schedule is active or not.
    - `active=false`, the schedule will be ignored at startup or removed at the next sync interval.
    - `active=true`, the schedule will be include at startup or added at the next sync interval.
* `name` - is a unique name for the schedule.
* `task` - is the import path of the task e.g. `test_app.beat1`, `test_app.beat2`.
* `type` - is the type of the schedule and supports two types: `cron` and `periodic`.
    - `cron` - is a crontab with timezone awareness.
    - `periodic` - is a schedule with a frequency of seconds from the `seconds` column.
* `last_scheduled_date` - is when the beat was last sent to be processed.

> NOTE: `last_scheduled_date` does not mean the task was successful or even if the task was processed.  It just means the scheduler sent a request at that time.

### Config

In your celery `app.conf` you'll need to set `beat_reloader_dburl` to the url of your database.

```python
# test_app.py
import celery

app = celery.Celery(
    "test",
    broker_url="redis://localhost:6379",
    timezone="UTC",
    beat_reloader_dburl="postgresql+psycopg2://user:pass@127.0.0.1:5432/db",
)


@app.task
def beat1():
    print("beat1")


@app.task
def beat2():
    print("beat2")

```

### Running

```bash
celery --app test_app beat -S celery_sql_beat_reloader:Reloader --max-interval=300 --loglevel=INFO
```

Specifying the `--max-interval` argument will allow you to control how frequently the schedule syncs with the database


## Acknowledgments

- [celery-sqlalchemy-scheduler](https://github.com/sir-wiggles/celery-sqlalchemy-scheduler)
- [django-celery-beat](https://github.com/celery/django-celery-beat)
- [celerybeatredis](https://github.com/liuliqiang/celerybeatredis)
- [celery](https://github.com/celery/celery)
