#!/usr/bin/env python
# -*- encoding:utf-8 -*-

import os.path

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import get_config

db_session = None


def get_uri():
    config = get_config()
    base_dir = config.get('general', 'base_dir')
    db_name = config.get('database', 'db_name')
    db_path = os.path.join(base_dir, db_name)
    uri = 'sqlite:///%s' % db_path
    return uri


def get_session():
    global db_session
    if db_session:
        return db_session
    db_engine = create_engine(get_uri(), echo=False)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                            autoflush=False,
                                            bind=db_engine))
    return db_session


def get_all_tables():
    tables = {}
    inspector = inspect(get_session().get_bind())
    for table_name in inspector.get_table_names():
        columns = []
        for column in inspector.get_columns(table_name):
            columns.append(column['name'])
        tables[table_name] = columns
    return tables
