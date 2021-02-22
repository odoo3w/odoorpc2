
import odoorpc

from odoorpc2.env import Environment


class ODOO(odoorpc.ODOO):
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
        return self._session_info

    def _get_virtual_id(self):
        int_virtual_id = self._virtual_id
        self._virtual_id = self._virtual_id + 1
        return 'virtual_%s' % (int_virtual_id)

    def login(self, db, login='admin', password='admin'):
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
