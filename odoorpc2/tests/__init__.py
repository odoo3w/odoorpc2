# -*- coding: UTF-8 -*-
try:
    import unittest2 as unittest
except:
    import unittest

import os

import odoorpc2 as odoorpc

from odoorpc2.tests.config import HOST, DB, USER, PWD


class BaseTestCase(unittest.TestCase):
    """Instanciates an ``odoorpc.ODOO`` object, nothing more."""

    def setUp(self):
        self.env = {'host': HOST, 'port': 8069,
                    'db': DB, 'user': USER, 'pwd': PWD}
        self.odoo = odoorpc.ODOO(
            self.env['host'], port=self.env['port'])


class LoginTestCase(BaseTestCase):
    """Instanciates an ``odoorpc.ODOO`` object and perform the user login."""

    def setUp(self):
        BaseTestCase.setUp(self)
        self.odoo.login(self.env['db'], self.env['user'], self.env['pwd'])
        self.user = self.odoo.env.user
        self.user_obj = self.odoo.env['res.users']

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
