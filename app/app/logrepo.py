#!/usr/bin/env python3

'''
This module abstract database operations through its LogRepo class.
'''

from tenacity import retry, wait_exponential, stop_after_attempt
import psycopg
from datetime import datetime
from app import resources as res
from typing import Callable


class LogRecord(object):
    '''
    A ORM of a database log record.
    '''

    def __init__(self, record: tuple):
        self.id: int = record[0]
        self.created: datetime = record[1]
        self.message: str = record[2]

    def __str__(self) -> str:
        return f'{self.created.strftime("%Y-%m-%d %H:%M:%S")} - {self.message}'


class LogRepo(object):
    '''
    An abstraction of the database's log table. This class vends a handful
    of utilities to insert and query this table.
    '''

    def __init__(self, dbhost: str, dbport: int, dbuser: str, dbpass: str):
        self.dbhost: str = dbhost
        self.dbport: int = dbport
        self.dbuser: str = dbuser
        self.dbpass: str = dbpass

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    def _connect(self) -> psycopg.Connection:
        return psycopg.connect(
            f'postgresql://{self.dbuser}:{self.dbpass}@{self.dbhost}:{self.dbport}/logs')

    def _insertlog(self, cursor: psycopg.Cursor, message: str) -> None:
        created = datetime.now()

        repartition = res.Q_LOG_PARTITION.format(
            created.strftime('%Y%m%d%H%M'),
            created.strftime('%Y-%m-%d %H:%M:00'),
            created.strftime('%Y-%m-%d %H:%M:59')
        )
        cursor.execute(repartition)
        cursor.execute(res.Q_LOG_INSERT, (created, message))

    def _fetchtables(self, cursor: psycopg.Cursor) -> list[str]:
        cursor.execute(res.Q_DT)
        # [('public', 'log', 'partitioned table', 'postgres'), ('public', 'log_def', 'table', 'postgres')]
        return [p[1] for p in cursor.fetchall()]

    def fetchlogs(self) -> list[LogRecord]:
        '''
        Retrieve a list of all logs.
        '''
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(res.Q_LOG_SELECT)
                logs = [LogRecord(r) for r in cur.fetchall()]
                self._insertlog(cur, f'Fetched {len(logs)} logs.')
                conn.commit()
                return logs

    def insertlog(self, message: str) -> None:
        '''
        Insert a log entry into the log table.
        '''
        with self._connect() as conn:
            with conn.cursor() as cursor:
                self._insertlog(cursor, message)
                conn.commit()

    def fetchtables(self) -> list[str]:
        '''
        Fetch all tables in the database.
        '''
        with self._connect() as conn:
            with conn.cursor() as cursor:
                tables = self._fetchtables(cursor)
                self._insertlog(cursor, f'Fetched {len(tables)} tables.')
                conn.commit()
                return tables

    def prunepartitions(self) -> list[str]:
        '''
        This method drops all but the latest log partition and the original log table.
        '''

        with self._connect() as conn:
            with conn.cursor() as cursor:
                tables = sorted(self._fetchtables(cursor))

                # Keep "log" and the last partition (it may both be "log")
                reserved = set((tables[0], tables[-1]))
                prune = list(filter(lambda t: t not in reserved, tables))

                for table in prune:
                    cursor.execute(res.Q_LOG_DROP_PARTITION.format(table))

                self._insertlog(cursor, f'Pruned {len(prune)} tables.')
                conn.commit()

                return prune
