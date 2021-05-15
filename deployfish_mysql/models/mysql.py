import os
import tempfile

from shellescape import quote

from deployfish.config import get_config
from deployfish.core.models import Manager, Model, Secret, Service


# ----------------------------------------
# Managers
# ----------------------------------------

class MySQLDatabaseManager(Manager):

    def get(self, pk):
        # hint: (str["{name}"])
        config = get_config()
        section = config.get_section('mysql')
        databases = {}
        for data in section:
            databases[data['name']] = data
        if pk in databases:
            return MySQLDatabase.new(databases[pk], 'deployfish')
        else:
            raise MySQLDatabase.DoesNotExist(
                'Could not find an MySQLDatabase config named "{}" in deployfish.yml:mysql'.format(pk)
            )

    def list(self, service_name=None):
        # hint: (str["{service_name}"], int)
        config = get_config()
        section = config.get_section('mysql')
        databases = [MySQLDatabase.new(db, 'deployfish') for db in section]
        if service_name:
            databases = [db for db in databases if db.data['service'] == service_name]
        return databases

    def delete(self, obj):
        raise self.ReadOnly('SSH Tunnel objects are read only.')

    def save(self, obj, root_user, root_password, ssh_target=None, verbose=False):
        return self.create(obj, root_user, root_password, ssh_target=ssh_target, verbose=verbose)

    def create(self, obj, root_user, root_password, verbose=False, ssh_target=None):
        command = obj.render_for_create().format(
            root_user=root_user,
            root_password=root_password
        )
        return obj.cluster.ssh_target.ssh_noninteractive(
            command,
            ssh_target=ssh_target,
            verbose=verbose
        )

    def validate(self, obj, ssh_target=None, verbose=False):
        command = obj.render_for_validate()
        return obj.cluster.ssh_target.ssh_noninteractive(
            command,
            ssh_target=ssh_target,
            verbose=verbose
        )

    def dump(self, obj, filename=None, ssh_target=None, verbose=False):
        if filename is None:
            filename = "{}.sql".format(obj.service.name)
            i = 1
            while os.path.exists(filename):
                filename = "{}-{}.sql".format(obj.service.name, i)
                i += 1
        command = obj.render_for_dump()
        tmp_fd, file_path = tempfile.mkstemp()
        with os.fdopen(tmp_fd, 'w') as fd:
            success, output = obj.cluster.ssh_target.ssh_noninteractive(
                command,
                output=fd,
                ssh_target=ssh_target,
                verbose=verbose
            )
            if success:
                fd.close()
                os.rename(file_path, filename)
                return success, output, filename
            else:
                fd.seek(0)
                errors = fd.read()
                raise self.OperationFailed('Dump of MySQLDatabase("{}") failed:\n{}'.format(obj.pk, errors))

    def load(self, obj, filepath, ssh_target=None, verbose=False):
        success, output, filename = obj.cluster.push_file(filepath)
        command = obj.render_for_load().format(filename=filename)
        return obj.cluster.ssh_target.ssh_noninteractive(command, ssh_target=ssh_target, verbose=verbose)


# ----------------------------------------
# Models
# ----------------------------------------

class MySQLDatabase(Model):
    """
    self.data here has the following structure:

        {
            'name': 'string',
            'service': 'string',
            'character_set': 'string',                   [optional, default='utf8']
            'collation': 'string',                       [optional, default='utf8_unicode_ci']
            'host': 'string',
            'db': 'string' ,
            'user': 'string',
            'pass': 'string',
            'port': 'string'                             [optional, default=3306]
        }
    """

    objects = MySQLDatabaseManager()
    config_section = 'mysql'

    @property
    def pk(self):
        return self.data['name']

    @property
    def name(self):
        return self.data['name']

    def secret(self, name):
        if 'secrets' not in self.cache:
            self.cache['secrets'] = {}
        if name not in self.cache['secrets']:
            if "." not in name:
                full_name = '{}{}'.format(self.service.secrets_prefix, name)
            else:
                full_name = name
            self.cache['secrets'][name] = Secret.objects.get(full_name)
        return self.cache['secrets'][name]

    def parse(self, key):
        """
        deployfish supports putting 'config.KEY' as the value for the host and port keys in self.data

        Parse the value and dereference it from the live secrets for the service if necessary.
        """
        if isinstance(self.data[key], str):
            if self.data[key].startswith('config.'):
                _, key = self.data[key].split('.')
                try:
                    value = self.secret(key).value
                except Secret.DoesNotExist:
                    raise self.OperationFailed(
                        'MySQLDatabase(pk="{}"): Service(pk="{}") has no secret named "{}"'.format(
                            self.name,
                            self.service.pk,
                            key
                        )
                    )
                return value
        return self.data[key]

    @property
    def host(self):
        if 'host' not in self.cache:
            self.cache['host'] = self.parse('host')
        return self.cache['host']

    @property
    def user(self):
        if 'user' not in self.cache:
            self.cache['user'] = self.parse('user')
        return self.cache['user']

    @property
    def db(self):
        if 'db' not in self.cache:
            self.cache['db'] = self.parse('db')
        return self.cache['db']

    @property
    def password(self):
        if 'password' not in self.cache:
            self.cache['password'] = self.parse('pass')
        return self.cache['password']

    @property
    def character_set(self):
        if 'character_set' not in self.cache:
            if 'character_set' not in self.data:
                self.cache['character_set'] = 'utf8'
            else:
                self.cache['character_set'] = self.parse('character_set')
        return self.cache['character_set']

    @property
    def collation(self):
        if 'collation' not in self.cache:
            if 'collation' not in self.data:
                self.cache['collation'] = 'utf8_unicode_ci'
            else:
                self.cache['collation'] = self.parse('collation')
        return self.cache['collation']

    @property
    def port(self):
        if 'port' not in self.cache:
            if 'port' not in self.data:
                self.cache['port'] = 3306
            else:
                self.cache['port'] = self.parse('port')
        return self.cache['port']

    @property
    def ssh_target(self):
        return self.service.ssh_target

    @property
    def ssh_targets(self):
        return self.service.ssh_targets

    @property
    def service(self):
        if 'service' not in self.cache:
            config = get_config()
            data = config.get_section_item('services', self.data['service'])
            # We don't need the live service; we just need the service's cluster to exist
            self.cache['service'] = Service.new(data, 'deployfish')
        return self.cache['service']

    @service.setter
    def service(self, value):
        self.cache['service'] = value

    @property
    def cluster(self):
        return self.service.cluster

    def create(self, root_user, root_password, ssh_target=None, verbose=False):
        return self.objects.create(self, root_user, root_password, ssh_target=ssh_target, verbose=verbose)

    def validate(self, ssh_target=None, verbose=False):
        return self.objects.validate(self, ssh_target=ssh_target, verbose=verbose)

    def dump(self, filename=None, ssh_target=None, verbose=False):
        return self.objects.dump(self, filename=filename, ssh_target=ssh_target, verbose=verbose)

    def load(self, filename, ssh_target=None, verbose=False):
        return self.objects.load(self, filename, ssh_target=ssh_target, verbose=verbose)

    def render_for_create(self):
        sql = "CREATE DATABASE {} CHARACTER SET {} COLLATE {};".format(self.db, self.character_set, self.collation)
        sql += "grant all privileges on {}.* to '{}'@'%' identified with mysql_native_password by '{}';".format(
            self.db,
            self.user,
            self.password
        )
        command = "/usr/bin/mysql --host={} --user={{root_user}} --password={{root_password}} --port={} --execute=\"{}\"".format(
            self.host, self.port, sql
        )
        return command

    def render_for_dump(self):
        cmd = "/usr/bin/mysqldump --host={host} --user={user} --password={password} --port={port} --opt {db}"
        cmd = cmd.format(
            host=self.host,
            user=self.user,
            password=self.password,
            port=self.port,
            db=self.db
        )
        return cmd

    def render_for_load(self):
        cmd = "/usr/bin/mysql --host={} --user={} --password={} --port={} {} < {{filename}}; rm {{filename}}".format(
            self.host,
            self.user,
            quote(self.password),
            self.port,
            self.name
        )
        return cmd

    def render_for_validate(self):
        cmd = "/usr/bin/mysql --host={} --user={} --password={} --port={} --execute='select version(), current_date;'"
        cmd = cmd.format(self.host, self.user, quote(self.password), self.port)
        return cmd
