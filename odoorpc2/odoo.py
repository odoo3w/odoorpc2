
# -*- coding: UTF-8 -*-
##############################################################################
#
#    OdooRPC2
#    Copyright (C) 2020 Master Zhang odoowww@163.com.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import odoorpc

from odoorpc2.env import Environment


class ODOO(odoorpc.ODOO):
    """Inherited form `odoorpc.ODOO`
    new api.

    .. doctest::
    >>> import odoorpc2
    >>> odoo = odoorpc2.ODOO('localhost', port=8069)  # connect to localhost, default port
    >>> odoo.login('dbname', 'admin', 'admin')
    >>> odoo.session_info

    `auto_commit` default value is True in odoorpc.ODOO 
    but False in odoorpc2.ODOO

    """

    def __init__(self, host='localhost', protocol='jsonrpc',
                 port=8069, timeout=120, version=None, opener=None):

        super().__init__(host=host, protocol=protocol,
                         port=port, timeout=timeout, version=version, opener=opener)

        # by default, auto_commit is False
        self.config['auto_commit'] = False
        self._session_info = {}
        self._virtual_id = 1

    @property
    def session_info(self):
        # after login, we store session in here
        return self._session_info

    def _get_virtual_id(self):
        # new a o2m field, need an unique virtual id
        int_virtual_id = self._virtual_id
        self._virtual_id = self._virtual_id + 1
        return 'virtual_%s' % (int_virtual_id)

    def login(self, db, login='admin', password='admin'):
        # after login, we gei session_info form odoo
        super().login(db, login=login, password=password)

        if self.env.uid:
            uid = self.env.uid
            db = self.env.db
            context = self.env.context
            self._env = Environment(self, db, uid, context=context)
            session_info = self.get_session_info()
            self._session_info = session_info

    def get_session_info(self):
        data = self.json('/web/session/get_session_info', {})
        return data['result']

    def test_rpc(self):
        data = self.json('/web2/test', {'file': '122', 'import_id': 0})
        return data['result']

    def test_rpc2(self):
        data = self.json('/web2/session/check', {})
        return data

    def print_dict(self, data_dict, name=None):
        print('-----------------', name)
        print('-----------------')
        print('-----------------')
        flds = [fld for fld in data_dict]
        flds.sort()
        for fld in flds:
            val = data_dict[fld]
            if isinstance(val, str):
                val = '"%s"' % val
            print('%s: %s' % (fld, val))
        print('-----------------', name)
        print('-----------------')


if __name__ == '__main__':
    odoo = ODOO('192.168.56.103')
    odoo.login('tiandi', 'admin', '123456')
