from esileapclient.tests.functional.base import ESIBaseTestClass
import esileapclient.tests.functional.utils.cinder_interfaces as cinder
from esileapclient.tests.functional.utils.dummy_node import DummyNode


class VolumeTests(ESIBaseTestClass):
    @classmethod
    def setUpClass(cls):
        super(VolumeTests, cls).setUpClass()
        cls._init_dummy_project(cls, 'owner', 'owner')
        cls._init_dummy_project(cls, 'lessee', 'lessee')

    def setUp(self):
        super(VolumeTests, self).setUp()
        self.clients = VolumeTests.clients
        self.users = VolumeTests.users
        self.projects = VolumeTests.projects
