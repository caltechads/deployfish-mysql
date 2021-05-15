import click

from deployfish.cli.adapters.utils import handle_model_exceptions, print_render_exception
from deployfish.config import get_config
from deployfish.exceptions import RenderException, ConfigProcessingFailed


class ClickCreateDatabaseCommandMixin(object):

    @classmethod
    def add_create_database_click_command(cls, command_group):
        """
        Build a fully specified click command for creating databases and users in MySQL servers, and add it
        to the command group `command_group`.  Return the properly wrapped function object.

        :param command_group function: the click command group function to use to register our click command

        :rtype: function
        """
        def create_database(ctx, *args, **kwargs):
            if cls.model.config_section is not None:
                try:
                    ctx.obj['config'] = get_config(**ctx.obj)
                except ConfigProcessingFailed as e:
                    ctx.obj['config'] = e
            ctx.obj['adapter'] = cls()
            click.secho(ctx.obj['adapter'].create_database(
                kwargs['identifier'],
                kwargs['root_user'],
                kwargs['root_password'],
                kwargs['choose'],
                kwargs['verbose']
            ))

        create_database.__doc__ = """
Create a database and user in a remote MySQL server for a Service.

IDENTIFIER is the name of the mysql connection in deployfish.yml.
"""

        function = print_render_exception(create_database)
        function = click.pass_context(function)
        function = click.option(
            '--root-user',
            default=None,
            envvar='DEPLOYFISH_MYSQL_MYSQL_ROOT_USER',
            help="The username of the root user for the remote MySQL server"

        )(function)
        function = click.option(
            '--root-password',
            default=None,
            envvar='DEPLOYFISH_MYSQL_MYSQL_ROOT_PASSWORD',
            help="The password of the root user for the remote MySQL server"
        )(function)
        function = click.option(
            '--verbose/--no-verbose',
            '-v',
            default=False,
            help="Show all SSH output."
        )(function)
        function = click.option(
            '--choose/--no-choose',
            '-v',
            default=False,
            help='Choose from all available ssh targets in our cluster, instead of having one chosen automatically.'
        )(function)
        function = click.argument('identifier')(function)
        function = command_group.command(
            'create',
            short_help='Create a MySQL database and user for a Service.'.format(
                object_name=cls.model.__name__
            )
        )(function)
        return function

    @handle_model_exceptions
    def create_database(self, identifier, root_user, root_password, choose, verbose):
        obj = self.get_object_from_deployfish(identifier)
        if not root_user:
            root_user = click.prompt('DB root user')
        if not root_password:
            root_password = click.prompt('DB root password')
        if choose:
            target = self.get_target(obj.cluster)
        else:
            target = None
        success, output = obj.create(root_user, root_password, ssh_target=target, verbose=verbose)
        if success:
            lines = []
            lines.append(click.style(
                'Created database "{}" in mysql server {}:{}.'.format(obj.db, obj.host, obj.port),
                fg='green'
            ))
            lines.append(click.style(
                'Created user "{}" in mysql server {}:{} and granted it all privileges on database "{}".'.format(
                    obj.user, obj.host, obj.port, obj.db
                ),
                fg='green'
            ))
            return '\n'.join(lines)
        else:
            raise RenderException('Failed to create database and/or user: {}'.format(output))


class ClickValidateDatabaseUserCommandMixin(object):

    @classmethod
    def add_validate_database_user_click_command(cls, command_group):
        """
        Build a fully specified click command for validating database users in MySQL servers, and add it
        to the command group `command_group`.  Return the properly wrapped function object.

        :param command_group function: the click command group function to use to register our click command

        :rtype: function
        """
        def validate_user(ctx, *args, **kwargs):
            if cls.model.config_section is not None:
                try:
                    ctx.obj['config'] = get_config(**ctx.obj)
                except ConfigProcessingFailed as e:
                    ctx.obj['config'] = e
            ctx.obj['adapter'] = cls()
            click.secho(ctx.obj['adapter'].validate_user(
                kwargs['identifier'],
                kwargs['choose'],
                kwargs['verbose']
            ))

        validate_user.__doc__ = """
Validate that a user in a remote MySQL server exists and has the password we expect.

IDENTIFIER is the name of the mysql connection in deployfish.yml.
"""

        function = print_render_exception(validate_user)
        function = click.pass_context(function)
        function = click.option(
            '--verbose/--no-verbose',
            '-v',
            default=False,
            help="Show all SSH output."
        )(function)
        function = click.option(
            '--choose/--no-choose',
            '-v',
            default=False,
            help='Choose from all available ssh targets in our cluster, instead of having one chosen automatically.'
        )(function)
        function = click.argument('identifier')(function)
        function = command_group.command(
            'validate',
            short_help='Validate that a MySQL user for a Service exists and has the password we expect.'.format(
                object_name=cls.model.__name__
            )
        )(function)
        return function

    @handle_model_exceptions
    def validate_user(self, identifier, choose, verbose):
        obj = self.get_object_from_deployfish(identifier)
        if choose:
            target = self.get_target(obj.cluster)
        else:
            target = None
        success, output = obj.validate(ssh_target=target, verbose=verbose)
        if success:
            lines = []
            lines.append(click.style(
                'MySQL user "{}" in mysql server {}:{} exists and has the password we expect.'.format(
                    obj.user, obj.host, obj.port
                ),
                fg='green'
            ))
            return '\n'.join(lines)
        else:
            raise RenderException('Failed to validate our MySQL user "{}" in {}:{}:  {}'.format(
                obj.user,
                obj.host,
                obj.port,
                output
            ))


class ClickDumpDatabaseCommandMixin(object):

    @classmethod
    def add_dump_database_click_command(cls, command_group):
        """
        Build a fully specified click command for dumping databases from MySQL servers, and add it
        to the command group `command_group`.  Return the properly wrapped function object.

        :param command_group function: the click command group function to use to register our click command

        :rtype: function
        """
        def validate_user(ctx, *args, **kwargs):
            if cls.model.config_section is not None:
                try:
                    ctx.obj['config'] = get_config(**ctx.obj)
                except ConfigProcessingFailed as e:
                    ctx.obj['config'] = e
            ctx.obj['adapter'] = cls()
            click.secho(ctx.obj['adapter'].dump_database(
                kwargs['identifier'],
                kwargs['filename'],
                kwargs['choose'],
                kwargs['verbose']
            ))

        validate_user.__doc__ = """
Dump the contents of a MySQL database to a local file.

IDENTIFIER is the name of the mysql connection in deployfish.yml.
"""

        function = print_render_exception(validate_user)
        function = click.pass_context(function)
        function = click.option(
            '--filename',
            default=None,
            help="Write SQL dump to this local file"
        )(function)
        function = click.option(
            '--verbose/--no-verbose',
            '-v',
            default=False,
            help="Show all SSH output."
        )(function)
        function = click.option(
            '--choose/--no-choose',
            '-v',
            default=False,
            help='Choose from all available ssh targets in our cluster, instead of having one chosen automatically.'
        )(function)
        function = click.argument('identifier')(function)
        function = command_group.command(
            'dump',
            short_help='Dump the contents of MySQL database to a local file.'.format(
                object_name=cls.model.__name__
            )
        )(function)
        return function

    @handle_model_exceptions
    def dump_database(self, identifier, filename, choose, verbose):
        obj = self.get_object_from_deployfish(identifier)
        if choose:
            target = self.get_target(obj.cluster)
        else:
            target = None
        success, output, output_filename = obj.dump(filename=filename, ssh_target=target, verbose=verbose)
        if success:
            lines = []
            lines.append(click.style(
                'Dumped database "{}" in mysql server {}:{} to "{}".'.format(
                    obj.db, obj.host, obj.port, output_filename
                ),
                fg='green'
            ))
            return '\n'.join(lines)
        else:
            raise RenderException('Failed to dump our MySQL db "{}" in {}:{}:  {}'.format(
                obj.db,
                obj.host,
                obj.port,
                output
            ))


class ClickLoadSQLCommandMixin(object):

    @classmethod
    def add_load_sql_click_command(cls, command_group):
        """
        Build a fully specified click command for loading local SQL files into a MySQL database, and add it
        to the command group `command_group`.  Return the properly wrapped function object.

        :param command_group function: the click command group function to use to register our click command

        :rtype: function
        """
        def validate_user(ctx, *args, **kwargs):
            if cls.model.config_section is not None:
                try:
                    ctx.obj['config'] = get_config(**ctx.obj)
                except ConfigProcessingFailed as e:
                    ctx.obj['config'] = e
            ctx.obj['adapter'] = cls()
            click.secho(ctx.obj['adapter'].load_sql(
                kwargs['identifier'],
                kwargs['filename'],
                kwargs['choose'],
                kwargs['verbose']
            ))

        validate_user.__doc__ = """
Load the contents of a local SQL file into an existing MySQL database.

IDENTIFIER is the name of the mysql connection in deployfish.yml.
"""

        function = print_render_exception(validate_user)
        function = click.pass_context(function)
        function = click.option(
            '--verbose/--no-verbose',
            '-v',
            default=False,
            help="Show all SSH output."
        )(function)
        function = click.option(
            '--choose/--no-choose',
            '-v',
            default=False,
            help='Choose from all available ssh targets in our cluster, instead of having one chosen automatically.'
        )(function)
        function = click.argument('filename')(function)
        function = click.argument('identifier')(function)
        function = command_group.command(
            'load',
            short_help='Dump the contents of MySQL database to a local file.'.format(
                object_name=cls.model.__name__
            )
        )(function)
        return function

    @handle_model_exceptions
    def load_sql(self, identifier, filename, choose, verbose):
        obj = self.get_object_from_deployfish(identifier)
        if choose:
            target = self.get_target(obj.cluster)
        else:
            target = None
        success, output = obj.load(filename, ssh_target=target, verbose=verbose)
        if success:
            lines = []
            lines.append(click.style(
                'Loaded file "{}" into database "{}" on  mysql server {}:{}'.format(
                    filename, obj.db, obj.host, obj.port
                ),
                fg='green'
            ))
            return '\n'.join(lines)
        else:
            raise RenderException('Failed to load our file "{}" into MySQL db "{}" in {}:{}:  {}'.format(
                filename,
                obj.db,
                obj.host,
                obj.port,
                output
            ))
