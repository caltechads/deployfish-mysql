import click
import os
from shellescape import quote

from deployfish.cli import cli
from deployfish.aws.ecs import Service
from deployfish.config import Config


@cli.group(short_help="Manage a remote MySQL database")
def mysql():
    pass


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


def _get_db_parameters(service):
    host = _get_environment_value_from_suffix(service, 'DEPLOYFISH_DB_HOST_SUFFIX')
    name = _get_environment_value_from_suffix(service, 'DEPLOYFISH_DB_NAME_SUFFIX')
    user = _get_environment_value_from_suffix(service, 'DEPLOYFISH_DB_USER_SUFFIX')
    passwd = _get_environment_value_from_suffix(service, 'DEPLOYFISH_DB_PASSWORD_SUFFIX')
    port = _get_environment_value_from_suffix(service, 'DEPLOYFISH_DB_PORT_SUFFIX', '3306')
    return host, name, user, passwd, port


@mysql.command('create', short_help="Create database and user")
@click.pass_context
@click.argument('service_name')
def create(ctx, service_name):
    service = Service(yml=Config(filename=ctx.obj['CONFIG_FILE'], env_file=ctx.obj['ENV_FILE']).get_service(service_name))

    host, name, user, passwd, port = _get_db_parameters(service)
    root = click.prompt('DB root user')
    rootpw = click.prompt('DB root password')

    cmd = "/usr/bin/mysql --host={} --user={} --password={} --port={} --execute=\"create database {}; grant all privileges on {}.* to '{}'@'%' identified by '{}';\"".format(host, root, rootpw, port, name, name, user, passwd)

    success, output = service.run_remote_script([cmd])
    # success, output = service.create_db(host, root, rootpw, name, user, passwd, port)
    print success
    print output


@mysql.command(short_help='Validate database and user')
@click.pass_context
@click.argument('service_name')
def validate(ctx, service_name):
    service = Service(yml=Config(filename=ctx.obj['CONFIG_FILE'], env_file=ctx.obj['ENV_FILE']).get_service(service_name))
    host, name, user, passwd, port = _get_db_parameters(service)
    cmd = "/usr/bin/mysql --host={} --user={} --password={} --port={} --execute='select version(), current_date;'"
    cmd = cmd.format(host, user, quote(passwd), port)
    success, output = service.run_remote_script([cmd])
    print success
    print output


@mysql.command('dump', short_help='Dump database')
@click.pass_context
@click.argument('service_name')
def dump(ctx, service_name):
    service = Service(yml=Config(filename=ctx.obj['CONFIG_FILE'], env_file=ctx.obj['ENV_FILE']).get_service(service_name))
    host, name, user, passwd, port = _get_db_parameters(service)

    cmd = "/usr/bin/mysqldump --host={} --user={} --password={} --port={} --opt {}"
    cmd = cmd.format(host, user, quote(passwd), port, name)
    success, tmp_file = service.run_remote_script([cmd], file_output=True)
    output_filename = "{}.sql".format(service.serviceName)
    i = 1
    while os.path.exists(output_filename):
        output_filename = "{}-{}.sql".format(service.serviceName, i)

    os.rename(tmp_file, os.path.join(os.getcwd(), output_filename))
    if success:
        click.secho("Saved mysqldump output to: ./{}".format(output_filename))
    else:
        click.secho("PROBLEM: {}".format(tmp_file))


@mysql.command('load', short_help='Load database')
@click.pass_context
@click.argument('service_name')
@click.argument('data_file')
@click.option('--force/--no-force', default=False, help="Since this operation is dangerous, you have to force it.")
def load(ctx, service_name, data_file, force):
    if not force:
        click.echo("You must use --force if you wish to overwrite the {} database.".format(service_name))
        return
    if not click.confirm("Are you sure you wish to overwrite the {} database?".format(service_name)):
        return
    service = Service(yml=Config(filename=ctx.obj['CONFIG_FILE'], env_file=ctx.obj['ENV_FILE']).get_service(service_name))
    host, name, user, passwd, port = _get_db_parameters(service)

    head, filename = os.path.split(data_file)
    input_file = open(data_file)
    service.push_remote_text_file(input_data=input_file)

    cmd = [
        "/usr/bin/mysql --host={} --user={} --password={} --port={} {} < {}".format(
            host, user, quote(passwd), port, name, filename),
        "rm {}".format(filename)
    ]
    success, output = service.run_remote_script(cmd)

    print success
    print output
