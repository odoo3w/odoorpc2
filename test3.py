# import odoorpc

# odoo = odoorpc.ODOO('192.168.56.103')
# print('version', odoo.version)
# # odoo.login('tiandi', 'admin', '123456')
# odoo.login('T2', 'admin', '123456')

import datetime


def test2():

    # M = odoo.env['ir.sequence.date_range']
    # ids = M.search([])

    # m = M.browse(ids)

    # print(m)

    # pass
    pattern = "%Y-%m-%d"

    def fn(val):
        dd = datetime.datetime.strptime(value, pattern).date()
        return dd

    value = '2021-12-31'
    dd = fn(value)
    print(dd, type(dd))

    value = False
    dd = fn(value)
    print(dd, type(dd))


test2()
