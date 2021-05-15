from pathlib import Path

from deployfish import TEMPLATE_PATHS
from deployfish.cli import cli

import deployfish_mysql.adapters  # noqa:F401
from .adapters import ClickMySQLDatabaseAdapter


TEMPLATE_PATHS.append(Path(__file__).parent / 'templates')


mysql_group = ClickMySQLDatabaseAdapter.add_command_group(cli, 'mysql')
mysql_create = ClickMySQLDatabaseAdapter.add_create_database_click_command(mysql_group)
mysql_list = ClickMySQLDatabaseAdapter.add_list_click_command(mysql_group)
mysql_info = ClickMySQLDatabaseAdapter.add_info_click_command(mysql_group)
mysql_dump = ClickMySQLDatabaseAdapter.add_dump_database_click_command(mysql_group)
mysql_load = ClickMySQLDatabaseAdapter.add_load_sql_click_command(mysql_group)
mysql_validate = ClickMySQLDatabaseAdapter.add_validate_database_user_click_command(mysql_group)
