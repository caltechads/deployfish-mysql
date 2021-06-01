from deployfish.cli.adapters import ClickModelAdapter

from .commands import (
    ClickCreateDatabaseCommandMixin,
    ClickUpdateDatabaseCommandMixin,
    ClickDumpDatabaseCommandMixin,
    ClickLoadSQLCommandMixin,
    ClickValidateDatabaseUserCommandMixin,
    ClickServerVersionCommandMixin,
    ClickShowGrantsCommandMixin,
)
from deployfish_mysql.models import MySQLDatabase


class ClickMySQLDatabaseAdapter(
    ClickCreateDatabaseCommandMixin,
    ClickUpdateDatabaseCommandMixin,
    ClickDumpDatabaseCommandMixin,
    ClickLoadSQLCommandMixin,
    ClickValidateDatabaseUserCommandMixin,
    ClickServerVersionCommandMixin,
    ClickShowGrantsCommandMixin,
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
