from typing import Type, Any, Dict

from cement import ex, shell
import click

from deployfish.controllers.crud import ReadOnlyCrudBase
from deployfish.controllers.network import get_ssh_target
from deployfish.controllers.utils import handle_model_exceptions
from deployfish.core.models import Model

from deployfish_mysql.models.mysql import MySQLDatabase


class MysqlController(ReadOnlyCrudBase):

    class Meta:
        label = "mysql"
        description = 'Work with MySQL Databases'
        help = 'Work with MySQL Databases'
        stacked_type = 'nested'

    model: Type[Model] = MySQLDatabase

    help_overrides: Dict[str, str] = {
        'info': 'Show details about an MySQL database connection',
        'exists': 'Show whether a MySQL database connection exists in deployfish.yml',
        'list': 'List available MySQL database connections from deployfish.yml',
    }

    info_template: str = 'detail--mysqldatabase.jinja2'

    list_ordering: str = 'Name'
    list_result_columns: Dict[str, Any] = {
        'Name': 'name',
        'Host': 'host',
        'DB': 'db',
        'User': 'user',
        'Password': 'password',
    }

    @ex(
        help="Create a MySQL database and user in the remote MySQL server.",
        arguments=[
            (['pk'], {'help': 'the name of the MySQL connection in deployfish.yml'}),
            (
                ['--root-user'],
                {
                    'help': 'the username of the root user for the MySQL server',
                    'default': None,
                    'dest': 'root_user'
                }
            ),
            (
                ['--root-password'],
                {
                    'help': 'the password of the root user for the MySQL server',
                    'default': None,
                    'dest': 'root_password'
                }
            ),
            (
                ['-c', '--choose'],
                {
                    'help': 'Choose from all available ssh targets instead of choosing one automatically.',
                    'default': False,
                    'dest': 'choose',
                    'action': 'store_true'
                }
            ),
            (
                ['-v', '--verbose'],
                {
                    'help': 'Show all SSH output.',
                    'default': False,
                    'dest': 'verbose',
                    'action': 'store_true'
                }
            ),
        ],
        description="""
Create a database and user in a remote MySQL server.
"""
    )
    @handle_model_exceptions
    def create(self):
        loader = self.loader(self)
        obj = loader.get_object_from_deployfish(self.app.pargs.pk)
        if not self.app.pargs.root_user:
            p = shell.Prompt('DB root user')
            self.app.pargs.root_user = p.prompt()
        if not self.app.pargs.root_password:
            p = shell.Prompt('DB root password')
            self.app.pargs.root_password = p.prompt()
        target = get_ssh_target(self.app, obj.cluster, choose=self.app.pargs.choose)
        output = obj.create(
            self.app.pargs.root_user,
            self.app.pargs.root_password,
            ssh_target=target,
            verbose=self.app.pargs.verbose
        )
        lines = [
            click.style(
                'Created database "{}" in mysql server {}:{}.'.format(obj.db, obj.host, obj.port),
                fg='green'
            ), click.style(
                'Created user "{}" in mysql server {}:{} and granted it all privileges on database "{}".'.format(
                    obj.user, obj.host, obj.port, obj.db
                ),
                fg='green'
            )
        ]
        if output:
            lines.append(click.style('\nMySQL output:\n', fg='yellow'))
            lines.append(output)
        self.app.print('\n'.join(lines))

    @ex(
        help="Update a MySQL database and user for in the remote MySQL server.",
        arguments=[
            (['pk'], {'help': 'the name of the MySQL connection in deployfish.yml'}),
            (
                ['--root-user'],
                {
                    'help': 'the username of the root user for the MySQL server',
                    'default': None,
                    'dest': 'root_user'
                }
            ),
            (
                ['--root-password'],
                {
                    'help': 'the password of the root user for the MySQL server',
                    'default': None,
                    'dest': 'root_password'
                }
            ),
            (
                ['-c', '--choose'],
                {
                    'help': 'Choose from all available ssh targets instead of choosing one automatically.',
                    'default': False,
                    'dest': 'choose',
                    'action': 'store_true'
                }
            ),
            (
                ['-v', '--verbose'],
                {
                    'help': 'Show all SSH output.',
                    'default': False,
                    'dest': 'verbose',
                    'action': 'store_true'
                }
            ),
        ],
        description="""
Update an existing database and user in a remote MySQL server.  This allows you
to change the database character set and collation, update the user's password
and update the GRANTs for the user.
"""
    )
    @handle_model_exceptions
    def update(self):
        loader = self.loader(self)
        obj = loader.get_object_from_deployfish(self.app.pargs.pk)
        if not self.app.pargs.root_user:
            p = shell.Prompt('DB root user')
            self.app.pargs.root_user = p.prompt()
        if not self.app.pargs.root_password:
            p = shell.Prompt('DB root password')
            self.app.pargs.root_password = p.prompt()
        target = get_ssh_target(self.app, obj.cluster, choose=self.app.pargs.choose)
        output = obj.update(
            self.app.pargs.root_user,
            self.app.pargs.root_password,
            ssh_target=target,
            verbose=self.app.pargs.verbose
        )
        lines = [
            click.style(
                'Updated database "{}" in mysql server {}:{}.'.format(obj.db, obj.host, obj.port),
                fg='green'
            ), click.style(
                'Created user "{}" in mysql server {}:{} and granted it all privileges on database "{}".'.format(
                    obj.user, obj.host, obj.port, obj.db
                ),
                fg='green'
            )
        ]
        if output:
            lines.append(click.style('\nMySQL output:\n', fg='yellow'))
            lines.append(output)
        self.app.print('\n'.join(lines))

    @ex(
        help="Validate that a MySQL database and user exists in the remote MySQL server and has the password we expect.",
        arguments=[
            (['pk'], {'help': 'the name of the MySQL connection in deployfish.yml'}),
            (
                ['-c', '--choose'],
                {
                    'help': 'Choose from all available ssh targets instead of choosing one automatically.',
                    'default': False,
                    'dest': 'choose',
                    'action': 'store_true'
                }
            ),
            (
                ['-v', '--verbose'],
                {
                    'help': 'Show all SSH output.',
                    'default': False,
                    'dest': 'verbose',
                    'action': 'store_true'
                }
            ),
        ],
        description="""
Validate that a database and user in a remote MySQL server exists in the remote
MySQL server and has the password we expect.
"""
    )
    @handle_model_exceptions
    def validate(self):
        loader = self.loader(self)
        obj = loader.get_object_from_deployfish(self.app.pargs.pk)
        target = get_ssh_target(self.app, obj.cluster, choose=self.app.pargs.choose)
        obj.validate(ssh_target=target, verbose=self.app.pargs.verbose)
        lines = [
            click.style(
                'MySQL user "{}" in mysql server {}:{} exists and has the password we expect.'.format(
                    obj.user, obj.host, obj.port
                ),
                fg='green'
            )
        ]
        self.app.print('\n'.join(lines))

    @ex(
        help="Dump the contents of a remote MySQL database to local file.",
        arguments=[
            (['pk'], {'help': 'the name of the MySQL connection in deployfish.yml'}),
            (
                ['--dumpfile'],
                {
                    'help': 'Write the SQL dump to this file.',
                    'default': None,
                    'dest': 'dumpfile',
                }
            ),
            (
                ['-c', '--choose'],
                {
                    'help': 'Choose from all available ssh targets instead of choosing one automatically.',
                    'default': False,
                    'dest': 'choose',
                    'action': 'store_true'
                }
            ),
            (
                ['-v', '--verbose'],
                {
                    'help': 'Show all SSH output.',
                    'default': False,
                    'dest': 'verbose',
                    'action': 'store_true'
                }
            ),
        ],
        description="""
Dump the contents of a MySQL database to a local file.  If "--filename" is not supplied,
the filename of the output file will be "{service-name}.sql". If that exists, then we will
use "{service-name}-1.sql", and if that exists "{service-name}-2.sql" and so on.
"""
    )
    @handle_model_exceptions
    def dump(self):
        loader = self.loader(self)
        obj = loader.get_object_from_deployfish(self.app.pargs.pk)
        target = get_ssh_target(self.app, obj.cluster, choose=self.app.pargs.choose)
        _, output_filename = obj.dump(
            filename=self.app.pargs.dumpfile,
            ssh_target=target,
            verbose=self.app.pargs.verbose
        )
        lines = [
            click.style(
                'Dumped database "{}" in mysql server {}:{} to "{}".'.format(
                    obj.db, obj.host, obj.port, output_filename
                ),
                fg='green'
            )
        ]
        self.app.print('\n'.join(lines))

    @ex(
        help="Load the contents of a local SQL file into an existing MySQL database.",
        arguments=[
            (['pk'], {'help': 'the name of the MySQL connection in deployfish.yml'}),
            (['filename'], {'help': 'the filename of the SQL file to load'}),
            (
                ['-c', '--choose'],
                {
                    'help': 'Choose from all available ssh targets instead of choosing one automatically.',
                    'default': False,
                    'dest': 'choose',
                    'action': 'store_true'
                }
            ),
            (
                ['-v', '--verbose'],
                {
                    'help': 'Show all SSH output.',
                    'default': False,
                    'dest': 'verbose',
                    'action': 'store_true'
                }
            ),
        ],
        description="""
Load the contents of a local SQL file into an existing MySQL database in the remote MySQL server.
"""
    )
    @handle_model_exceptions
    def load(self):
        loader = self.loader(self)
        obj = loader.get_object_from_deployfish(self.app.pargs.pk)
        target = get_ssh_target(self.app, obj.cluster, choose=self.app.pargs.choose)
        output = obj.load(self.app.pargs.filename, ssh_target=target, verbose=self.app.pargs.verbose)
        lines = [
            click.style(
                'Loaded file "{}" into database "{}" on mysql server {}:{}'.format(
                    self.app.pargs.filename, obj.db, obj.host, obj.port
                ),
                fg='green'
            )
        ]
        if output.strip():
            # This is here just case `mysql` returns 0 but also prints something. Should probably never trigger.
            lines.append(click.style('Output from `mysql` command:\n{}'.format(output), fg='red'))
        self.app.print('\n'.join(lines))

    @ex(
        help="Show the GRANTs for the our user in the remote MySQL server.",
        arguments=[
            (['pk'], {'help': 'the name of the MySQL connection in deployfish.yml'}),
            (
                ['-c', '--choose'],
                {
                    'help': 'Choose from all available ssh targets instead of choosing one automatically.',
                    'default': False,
                    'dest': 'choose',
                    'action': 'store_true'
                }
            ),
            (
                ['-v', '--verbose'],
                {
                    'help': 'Show all SSH output.',
                    'default': False,
                    'dest': 'verbose',
                    'action': 'store_true'
                }
            ),
        ],
        description="""
Show the GRANTs for our user in the remote MySQL server.
"""
    )
    @handle_model_exceptions
    def show_grants(self):
        loader = self.loader(self)
        obj = loader.get_object_from_deployfish(self.app.pargs.pk)
        target = get_ssh_target(self.app, obj.cluster, choose=self.app.pargs.choose)
        output = obj.show_grants(ssh_target=target, verbose=self.app.pargs.verbose)
        self.app.print(output)

    @ex(
        help="Show the the MySQL version for the remote MySQL server.",
        arguments=[
            (['pk'], {'help': 'the name of the MySQL connection in deployfish.yml'}),
            (
                ['-c', '--choose'],
                {
                    'help': 'Choose from all available ssh targets instead of choosing one automatically.',
                    'default': False,
                    'dest': 'choose',
                    'action': 'store_true'
                }
            ),
            (
                ['-v', '--verbose'],
                {
                    'help': 'Show all SSH output.',
                    'default': False,
                    'dest': 'verbose',
                    'action': 'store_true'
                }
            ),
        ],
        description="""
Print the MySQL version of the remote MySQL server.
"""
    )
    @handle_model_exceptions
    def server_version(self):
        loader = self.loader(self)
        obj = loader.get_object_from_deployfish(self.app.pargs.pk)
        target = get_ssh_target(self.app, obj.cluster, choose=self.app.pargs.choose)
        self.app.print(obj.server_version(ssh_target=target, verbose=self.app.pargs.verbose))
