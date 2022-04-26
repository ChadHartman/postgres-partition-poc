#!/usr/bin/env python3

'''
This module loads static file resources.
'''


from importlib.resources import files


def _load(script: str) -> str:
    return files('resources').joinpath(script).read_text(encoding='utf-8')


Q_DT = _load('dt.sql')
Q_LOG_INSERT = _load('log-insert.sql')
Q_LOG_PARTITION = _load('log-partition.sql')
Q_LOG_SELECT = _load('log-select.sql')
Q_LOG_DROP_PARTITION = _load('log-drop-partition.sql')
