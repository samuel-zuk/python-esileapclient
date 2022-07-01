import os
import json
import configparser
from tempest.lib.cli import base
from tempest.lib.common.utils import data_utils
from tempest.lib.exceptions import CommandFailed


class ESIBaseTestClass(base.ClientTestBase):
    # TODO: refactor this to follow tempest style guide (no setUpClass)
    @classmethod
    def setUpClass(cls):
        super(ESIBaseTestClass, cls).setUpClass()
        cls.config = {}
        cls.users = {}
        cls.projects = {}
        cls.clients = {}
        cls._cls_cleanups = []

        cls._init_config(cls)
        cls._init_client(cls, 'admin', 'admin')
        cls._init_roles(cls)

    @classmethod
    def tearDownClass(cls):
        cls._cls_cleanups.reverse()
        for cleanup in cls._cls_cleanups:
            cleanup[0](*cleanup[1:])

    def _get_clients(self):
        # NOTE: ClientTestBase requires this to be implemented, but to
        # initialize our clients, we need ClientTestBase's constructor to have
        # been called. We return nothing leave the job on to _init_clients().
        return {}

    def _init_config(self):
        venv_name = os.environ.get('VENV_NAME', default='functional')
        self.config['cli_dir'] = (
            os.path.join(os.path.abspath('.'), '.tox/%s/bin' % venv_name))

        # allow custom configuration to be passed in via env var
        cfg_file_path = (
            os.environ.get('OS_ESI_CFG_PATH', '/etc/esi-leap/esi-leap.conf'))
        cfg_parser = configparser.ConfigParser()
        if not cfg_parser.read(cfg_file_path):
            self.fail('Could not open config file %s for reading' %
                      cfg_file_path)

        auth_opts = {}
        # main cfg parsing loop
        try:
            if cfg_parser.has_section('dummy_node'):
                opt = 'dummy_node_dir'
                self.config[opt] = cfg_parser.get('dummy_node', opt)
            # TODO: add support for keystone v2 (this is v3-only atm)

            # attempts to read authentication credentials in this order:
            # 1) [keystone] section of config file
            # 2) [keystone_authtoken] section of config file
            # 3) from the environment variables (e.g. OS_PASSWORD, etc)
            for opt in ('username', 'password', 'project_name', 'auth_type',
                        'auth_url', 'user_domain_name', 'project_domain_name'):
                for sect in 'keystone', 'keystone_authtoken':
                    if cfg_parser.has_option(sect, opt):
                        auth_opts[opt] = cfg_parser.get(sect, opt)
                        break
                if opt not in auth_opts.keys():
                    x = os.environ.get('OS_%s' % opt.upper())
                    if x is not None:
                        auth_opts[opt] = x
                    else:
                        raise configparser.NoOptionerror
        except (configparser.NoOptionError):
            self.fail("Missing option %s in configuration file." % opt)

        self.config['auth_type'] = auth_opts['auth_type']
        self.config['auth_url'] = auth_opts['auth_url']

        self.users['admin'] = {
            'name': auth_opts['username'],
            'password': auth_opts['password'],
            'domain': auth_opts['user_domain_name']
        }
        self.projects['admin'] = {
            'name': auth_opts['project_name'],
            'domain': auth_opts['project_domain_name']
        }

    def _init_client(self, user, project):
        self.clients[user] = (
            ESICLIClient(cli_dir=self.config['cli_dir'],
                         username=self.users[user]['name'],
                         password=self.users[user]['password'],
                         user_domain_name=self.users[user]['domain'],
                         tenant_name=self.projects[project]['name'],
                         project_domain_name=self.projects[project]['domain'],
                         uri=self.config['auth_url']))

    def _init_dummy_project(self, name, roles, parent=None):
        admin_client = self.clients['admin']

        # NOTE: names created using tempest's data_utils.rand_name() function
        #       will be prefixed with 'tempest-' and suffixed with randomly
        #       generated characters to prevent name collision.
        project_name = data_utils.rand_name('esi-%s-project' % name)
        flags = '--domain default --enable -f json'
        if parent:
            if parent not in self.projects.keys():
                raise NameError('Invalid parent project: %s' % parent)
            flags += ' --parent %s' % self.projects[parent]['name']
        output = admin_client.openstack('project create %s' % project_name,
                                        '', flags)
        self._cls_cleanups.append([admin_client.openstack, 'project delete',
                                   '', '%s' % project_name])
        project_id = json.loads(output)['id']
        self.projects[name] = {
            'name': project_name,
            'id': project_id,
            'parent': parent,
            'domain': 'default'
        }

        if roles is []:
            raise ValueError('No roles specified when initializing dummy \
                              project %s' % name)
        elif type(roles) is str:
            roles = [roles]

        for role in roles:
            if role not in ('owner', 'lessee', 'member'):
                raise ValueError('Unknown role: %s' % role)

            username = data_utils.rand_name('esi-%s-%s' % (name, role))
            password = data_utils.rand_password()
            output = admin_client.openstack('user create %s' % username, '',
                                            '--domain default --password %s \
                                             --enable -f json' % password)
            self._cls_cleanups.append([admin_client.openstack, 'user delete',
                                       '', '%s' % username])
            user_id = json.loads(output)['id']

            client_name = '%s-%s' % (name, role)
            self.users[client_name] = {
                'name': username,
                'id': user_id,
                'password': password,
                'domain': 'default'
            }

            if role != 'member':
                role = 'esi_leap_%s' % role
            admin_client.openstack('role add', '', '--user %s --project %s %s'
                                   % (username, project_name, role))
            self._cls_cleanups.append([admin_client.openstack, 'role remove',
                                       '', '--user %s --project %s %s' %
                                       (username, project_name, role)])

            self._init_client(self, client_name, name)

    def _init_roles(self):
        # TODO: find a way to make this play nice when running parallel tests.
        for role in 'esi_leap_owner', 'esi_leap_lessee':
            try:
                self.clients['admin'].openstack('role show', '', '%s' % role)
            except CommandFailed:
                self.clients['admin'].openstack('role create', '', '%s' % role)
                self._cls_cleanups.append([self.clients['admin'].openstack,
                                           'role delete', '',
                                           '%s' % role])


class ESICLIClient(base.CLIClient):
    def esi(self, action, flags='', params='', fail_ok=False,
            merge_stderr=False):
        return self.openstack('esi %s' % action, '',
                              '%s %s' % (flags, params),
                              fail_ok,
                              merge_stderr)
