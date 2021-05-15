from deployfish.cli.adapters import ClickModelAdapter

from .commands import (
    ClickCreateDatabaseCommandMixin,
    ClickDumpDatabaseCommandMixin,
    ClickLoadSQLCommandMixin,
    ClickValidateDatabaseUserCommandMixin,
)
from deployfish_mysql.models import MySQLDatabase


class ClickMySQLDatabaseAdapter(
    ClickCreateDatabaseCommandMixin,
    ClickDumpDatabaseCommandMixin,
    ClickLoadSQLCommandMixin,
    ClickValidateDatabaseUserCommandMixin,
    ClickModelAdapter
):

    model = MySQLDatabase

    list_ordering = 'Name'
    list_result_columns = {
        'Name': 'name',
        'Host': 'host',
        'DB': 'db',
        'User': 'user',
        'Password': 'password',
    }
