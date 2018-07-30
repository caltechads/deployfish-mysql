from __future__ import print_function

import click
import os
from shellescape import quote

from deployfish.aws.ecs import Service
from deployfish.cli import cli
from deployfish.config import Config, needs_config


@cli.group(short_help="Manage a remote MySQL database")
def mysql():
    """
    Manage a remote MySQL database

    The configuration for these commands should be found in a mysql: top-level section
    in the yaml file, in the format:

    \b
    mysql:
      - name: my_mysql_connection
        service: my_service
        host: config.MY_DB_HOST
        db: config.MY_DB_NAME
        user: config.MY_DB_USER
        pass: config.MY_DB_PASSWORD

    where the config.* values are the values define for this service in the AWS
    Parameter Store. These values could also just be the actual values rather than
    referring to the service's config values.
    """

def _interpolate_mysql_info(value, service):
    if type(value) == str and value.startswith('config.'):
        param_key = value[7:]
        for param in service.get_config():
            if param.key == param_key:
                return param.aws_value
    return value


def _get_environment_value_from_suffix(service, suffix, default=None):
    env_suffix = os.environ.get(suffix, None)
    if env_suffix:
        for param in service.get_config():
            if param.key.endswith(env_suffix):
                try:
                    return param.aws_value
                except:
                    return param.value
    return default


def _get_db_parameters(service, yml):
    host = _interpolate_mysql_info(yml['host'], service)
    name = _interpolate_mysql_info(yml['db'], service)
    user = _interpolate_mysql_info(yml['user'], service)
    passwd = _interpolate_mysql_info(yml['pass'], service)
    port = _interpolate_mysql_info(yml.get('port', '3306'), service)
    return host, name, user, passwd, port


@mysql.command('create', short_help="Create database and user")
@click.pass_context
@click.argument('name')
@needs_config
def create(ctx, name):
    yml = ctx.obj['CONFIG'].get_section_item('mysql', name)
    service = Service(yml['service'], config=ctx.obj['CONFIG'])

    host, name, user, passwd, port = _get_db_parameters(service, yml)
    root = click.prompt('DB root user')
    rootpw = click.prompt('DB root password')

    # NOTE: Best practice is to no longer use utf8, but rather utf8mb4. Unfortunately, that's not compatible with
    # django (yet), because it uses several indexed fields that are longer than 191 characters, which is the longest
    # that an indexed field can be in the utf8mb4 encoding (for stupid MySQL reasons). So we're still using utf8.
    # @see https://code.djangoproject.com/ticket/18392 and https://github.com/django/django/pull/8886
    exec1 = "CREATE DATABASE {} CHARACTER SET utf8 COLLATE utf8_unicode_ci;".format(name)
    exec2 = "grant all privileges on {}.* to '{}'@'%' identified by '{}';".format(name, user, passwd)
    cmd = "/usr/bin/mysql --host={} --user={} --password={} --port={} --execute=\"{} {}\"".format(
        host, root, rootpw, port, exec1, exec2
    )

    success, output = service.run_remote_script([cmd])
    print(success)
    print(output)


@mysql.command(short_help='Validate database and user')
@click.pass_context
@click.argument('name')
@needs_config
def validate(ctx, name):
    yml = ctx.obj['CONFIG'].get_section_item('mysql', name)
    service = Service(yml['service'], config=ctx.obj['CONFIG'])

    host, name, user, passwd, port = _get_db_parameters(service, yml)
    cmd = "/usr/bin/mysql --host={} --user={} --password={} --port={} --execute='select version(), current_date;'"
    cmd = cmd.format(host, user, quote(passwd), port)
    success, output = service.run_remote_script([cmd])
    print(success)
    print(output)


@mysql.command('dump', short_help='Dump database')
@click.pass_context
@click.argument('name')
@needs_config
def dump(ctx, name):
    yml = ctx.obj['CONFIG'].get_section_item('mysql', name)
    service = Service(yml['service'], config=ctx.obj['CONFIG'])
    host, name, user, passwd, port = _get_db_parameters(service, yml)

    cmd = "/usr/bin/mysqldump --host={} --user={} --password={} --port={} --opt {}"
    cmd = cmd.format(host, user, quote(passwd), port, name)
    success, tmp_file = service.run_remote_script([cmd], file_output=True)
    output_filename = "{}.sql".format(service.serviceName)
    i = 1
    while os.path.exists(output_filename):
        output_filename = "{}-{}.sql".format(service.serviceName, i)
        i += 1

    os.rename(tmp_file, os.path.join(os.getcwd(), output_filename))
    if success:
        click.secho("Saved mysqldump output to: ./{}".format(output_filename))
    else:
        click.secho("PROBLEM: {}".format(tmp_file))


@mysql.command('load', short_help='Load database')
@click.pass_context
@click.argument('name')
@click.argument('data_file')
@click.option('--force/--no-force', default=False, help="Since this operation is dangerous, you have to force it.")
@needs_config
def load(ctx, name, data_file, force):
    yml = ctx.obj['CONFIG'].get_section_item('mysql', name)
    if not force:
        click.echo("You must use --force if you wish to overwrite the {} database.".format(yml['service']))
        return
    if not click.confirm("Are you sure you wish to overwrite the {} database?".format(yml['service'])):
        return
    service = Service(yml['service'], config=ctx.obj['CONFIG'])

    host, name, user, passwd, port = _get_db_parameters(service, yml)

    head, filename = os.path.split(data_file)
    input_file = open(data_file)
    service.push_remote_text_file(input_data=input_file)

    cmd = [
        "/usr/bin/mysql --host={} --user={} --password={} --port={} {} < {}".format(
            host, user, quote(passwd), port, name, filename),
        "rm {}".format(filename)
    ]
    success, output = service.run_remote_script(cmd)

    print(success)
    print(output)
