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
            short_help='Create a MySQL database and user for a Service.'
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
        output = obj.create(root_user, root_password, ssh_target=target, verbose=verbose)
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
        if output:
            lines.append(click.style('\nMySQL output:\n', fg='yellow'))
            lines.append(output)
        return '\n'.join(lines)


class ClickUpdateDatabaseCommandMixin(object):

    @classmethod
    def add_update_database_click_command(cls, command_group):
        """
        Build a fully specified click command for creating databases and users in MySQL servers, and add it
        to the command group `command_group`.  Return the properly wrapped function object.

        :param command_group function: the click command group function to use to register our click command

        :rtype: function
        """
        def update_database(ctx, *args, **kwargs):
            if cls.model.config_section is not None:
                try:
                    ctx.obj['config'] = get_config(**ctx.obj)
                except ConfigProcessingFailed as e:
                    ctx.obj['config'] = e
            ctx.obj['adapter'] = cls()
            click.secho(ctx.obj['adapter'].update_database(
                kwargs['identifier'],
                kwargs['root_user'],
                kwargs['root_password'],
                kwargs['choose'],
                kwargs['verbose']
            ))

        update_database.__doc__ = """
Update an existing database and user in a remote MySQL server for a Service.  This allows you
to change the database character set and collation, update the user's password and update the
GRANTs for the user.

IDENTIFIER is the name of the mysql connection in deployfish.yml.
"""

        function = print_render_exception(update_database)
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
            '--verbose/--no-verbose'
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
            'update',
            short_help='Update a MySQL database and user for a Service.'
        )(function)
        return function

    @handle_model_exceptions
    def update_database(self, identifier, root_user, root_password, choose, verbose):
        obj = self.get_object_from_deployfish(identifier)
        if not root_user:
            root_user = click.prompt('DB root user')
        if not root_password:
            root_password = click.prompt('DB root password')
        if choose:
            target = self.get_target(obj.cluster)
        else:
            target = None
        output = obj.update(root_user, root_password, ssh_target=target, verbose=verbose)
        lines = []
        lines.append(click.style(
            'Updated database "{}" in mysql server {}:{}.'.format(obj.db, obj.host, obj.port),
            fg='green'
        ))
        lines.append(click.style(
            'Updated user "{}" in mysql server {}:{} and granted it all privileges on database "{}".'.format(
                obj.user, obj.host, obj.port, obj.db
            ),
            fg='green'
        ))
        if output:
            lines.append(click.style('\nMySQL output:\n', fg='yellow'))
            lines.append(output)
        return '\n'.join(lines)


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
            short_help='Validate that a MySQL user for a Service exists and has the password we expect.'
        )(function)
        return function

    @handle_model_exceptions
    def validate_user(self, identifier, choose, verbose):
        obj = self.get_object_from_deployfish(identifier)
        if choose:
            target = self.get_target(obj.cluster)
        else:
            target = None
        obj.validate(ssh_target=target, verbose=verbose)
        lines = []
        lines.append(click.style(
            'MySQL user "{}" in mysql server {}:{} exists and has the password we expect.'.format(
                obj.user, obj.host, obj.port
            ),
            fg='green'
        ))
        return '\n'.join(lines)


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
        output, output_filename = obj.dump(filename=filename, ssh_target=target, verbose=verbose)
        lines = []
        lines.append(click.style(
            'Dumped database "{}" in mysql server {}:{} to "{}".'.format(
                obj.db, obj.host, obj.port, output_filename
            ),
            fg='green'
        ))
        return '\n'.join(lines)


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
            short_help='Dump the contents of MySQL database to a local file.'
        )(function)
        return function

    @handle_model_exceptions
    def load_sql(self, identifier, filename, choose, verbose):
        obj = self.get_object_from_deployfish(identifier)
        if choose:
            target = self.get_target(obj.cluster)
        else:
            target = obj.cluster.ssh_target
        obj.load(filename, ssh_target=target, verbose=verbose)
        lines = []
        lines.append(click.style(
            'Loaded file "{}" into database "{}" on  mysql server {}:{}'.format(
                filename, obj.db, obj.host, obj.port
            ),
            fg='green'
        ))
        return '\n'.join(lines)


class ClickShowGrantsCommandMixin(object):

    @classmethod
    def add_show_grants_click_command(cls, command_group):
        """
        Build a fully specified click command for showing the MySQL grants for our user in the remote server, and add it
        to the command group `command_group`.  Return the properly wrapped function object.

        :param command_group function: the click command group function to use to register our click command

        :rtype: function
        """
        def show_grants(ctx, *args, **kwargs):
            if cls.model.config_section is not None:
                try:
                    ctx.obj['config'] = get_config(**ctx.obj)
                except ConfigProcessingFailed as e:
                    ctx.obj['config'] = e
            ctx.obj['adapter'] = cls()
            click.secho(ctx.obj['adapter'].get_grants_for_user(
                kwargs['identifier'],
                kwargs['choose'],
                kwargs['verbose']
            ))

        show_grants.__doc__ = """
Print the version of the remote MySQL Server for our Service.

IDENTIFIER is the name of the mysql connection in deployfish.yml.
"""

        function = print_render_exception(show_grants)
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
            'show-grants',
            short_help='Print the GRANTs for our user in the remote server.'
        )(function)
        return function

    @handle_model_exceptions
    def get_grants_for_user(self, identifier, choose, verbose):
        obj = self.get_object_from_deployfish(identifier)
        if choose:
            target = self.get_target(obj.cluster)
        else:
            target = None
        return obj.show_grants(ssh_target=target, verbose=verbose)


class ClickServerVersionCommandMixin(object):

    @classmethod
    def add_server_version_click_command(cls, command_group):
        """
        Build a fully specified click command for printing the MySQL version of the server, and add it
        to the command group `command_group`.  Return the properly wrapped function object.

        :param command_group function: the click command group function to use to register our click command

        :rtype: function
        """
        def server_version(ctx, *args, **kwargs):
            if cls.model.config_section is not None:
                try:
                    ctx.obj['config'] = get_config(**ctx.obj)
                except ConfigProcessingFailed as e:
                    ctx.obj['config'] = e
            ctx.obj['adapter'] = cls()
            click.secho(ctx.obj['adapter'].get_mysql_version(
                kwargs['identifier'],
                kwargs['choose'],
                kwargs['verbose']
            ))

        server_version.__doc__ = """
Print the version of the remote MySQL Server for our Service.

IDENTIFIER is the name of the mysql connection in deployfish.yml.
"""

        function = print_render_exception(server_version)
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
            'server-version',
            short_help='Print the MySQL version of the remote server.'
        )(function)
        return function

    @handle_model_exceptions
    def get_mysql_version(self, identifier, choose, verbose):
        obj = self.get_object_from_deployfish(identifier)
        if choose:
            target = self.get_target(obj.cluster)
        else:
            target = None
        return obj.server_version(ssh_target=target, verbose=verbose)
