# -*- coding: UTF-8 -*-


from odoorpc2.tests import BaseTestCase, LoginTestCase

import odoorpc2
import odoorpc


class TestODOO(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    def test_inherite(self):
        # print('in test2')
        self.assertTrue(isinstance(self.odoo, odoorpc2.ODOO))
        self.assertTrue(isinstance(self.odoo, odoorpc.ODOO))
        self.assertFalse(self.odoo.config['auto_commit'])
        self.assertNotIn('uid', self.odoo.session_info)


class TestLogin(LoginTestCase):
    def setUp(self):
        LoginTestCase.setUp(self)

    def test_login(self):
        self.assertEqual(self.user.login, 'admin')

    def test_session_info(self):
        self.assertIn('uid', self.odoo.session_info)
        self.assertEqual(self.odoo.session_info.get('username'), 'admin')

    # def test_env(self):
    #     print(self.odoo.env)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
