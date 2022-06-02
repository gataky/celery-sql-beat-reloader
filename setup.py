from os import path
from codecs import open

try:
    from setuptools import find_packages, setup
except ImportError:
    from distutils.core import setup, find_packages

basedir = path.abspath(path.dirname(__file__))
with open(path.join(basedir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="celery_sql_beat_reloader",
    version="0.0.1",
    url="https://github.com/sir-wiggles/celery-sql-beat-reloader",
    license="MIT",
    description="A Celery beat scheduler in SQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms="any",
    author="Jeff",
    author_email="jeffmgreg@gmail.com",
    home_page="https://github.com/sir-wiggles/celery-sql-beat-reloader",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="celery beat scheduler sql",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=[
        "celery>=5.2",
        "sqlalchemy",
    ],
    zip_safe=False,
)
