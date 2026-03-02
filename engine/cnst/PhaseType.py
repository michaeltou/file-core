from enum import Enum


class PhaseType(Enum):
    #
    ALL = 'all'
    #
    LOAD = 'load'
    #
    PROCESS = 'process'
    #
    FILTER = 'filter'
    #
    WRITE_2_DB = 'write_2_db'


