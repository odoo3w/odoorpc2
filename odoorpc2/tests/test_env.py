
from odoorpc2.tests import LoginTestCase
from odoorpc2.env import Environment
from odoorpc.env import Environment as odoorpc_Environment

from odoorpc2.models import Model

from odoorpc.models import MetaModel

from odoorpc2.fields import BaseField


class TestEnvironment(LoginTestCase):

    def test_env_init(self):
        env = self.odoo.env
        # print('test_env_init', env)
        self.assertIsInstance(env, odoorpc_Environment)
        self.assertIsInstance(env, Environment)

    def test_env_copy(self):
        env = self.odoo.env
        odoorpc_env = super(Environment, env)
        odoorpc_env2 = odoorpc_env.__call__()
        env2 = env()

        self.assertIsInstance(env2, Environment)
        self.assertIsInstance(odoorpc_env2, odoorpc_Environment)
        self.assertFalse(isinstance(odoorpc_env2, Environment))

    def test_env_create_model(self):
        Partner = self.odoo.env['res.partner']
        print(Partner)
        self.assertTrue(hasattr(Partner, '_model_id'))
        self.assertIsInstance(Partner, MetaModel)
        self.assertIsInstance(Partner._columns['name'], BaseField)

    def test_env_create_model_old(self):
        env = self.odoo.env
        odoorpc_env = super(Environment, env)
        odoorpc_env2 = odoorpc_env.__call__()
        Partner = odoorpc_env2['res.partner']
        print(Partner)
        self.assertFalse(hasattr(Partner, '_model_id'))
        self.assertNotIsInstance(Partner._columns['name'], BaseField)
