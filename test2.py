import odoorpc2

# import logging
# logging.basicConfig()
# logger = logging.getLogger('odoorpc')
# logger.setLevel(logging.DEBUG)


def print2(*args):
    print('in test2 ---------- :', *args)


def print_dict(data_dict, name=None):
    print('----', name)
    flds = [fld for fld in data_dict]
    flds.sort()
    for fld in flds:
        print('%s: %s' % (fld, data_dict[fld]))


odoo = odoorpc2.ODOO('192.168.56.103')
print2('version', odoo.version)
# odoo.login('tiandi', 'admin', '123456')
odoo.login('T2', 'admin', '123456')


def test1():
    model = 'res.partner'
    ref_str = 'base.view_partner_short_form'
    ref_str = 'base.view_partner_form'

    view = odoo.env.ref(ref_str)

    view_id = view.id

    P = odoo.env[model]
    res = P.fields_view_get(view_id)

    field_onchange1 = _onchange_spec(res)
    print(field_onchange1)

    # ids = []
    # values = {
    #     'is_company': True,
    #     'company_type': False
    # }

    # field_name = 'is_company'
    # field_onchange = field_onchange1

    # res = P.onchange([], values, field_name, field_onchange)

    # print(res)

    # print(res.keys())

    # for k, v in res.items():
    #     print(k, v)


def get_allowed_company_ids():
    session_info = odoo.session_info
    # print2('session_info', session_info)

    user_companies = session_info['user_companies']
    # print2(user_companies)

    allowed_companies = user_companies['allowed_companies']
    # print2(allowed_companies)
    allowed_company_ids = [com[0] for com in allowed_companies]
    return allowed_company_ids


def test_create_so():
    print2(' test start')
    model = 'sale.order'
    # model = 'ir.model'
    Model = odoo.env[model]
    print2(Model)
    # print2(Model._columns)
    # # print(Model.env)

    context2 = {
        'allowed_company_ids': get_allowed_company_ids(),
    }

    context = {}
    context.update(Model.env.context)
    context.update(context2)

    SO = Model.with_context(context)
    print2(SO)

    view_form_xml_id = 'sale.view_order_form'
    so = SO.browse(None, view_form_xml_id=view_form_xml_id)

    print2('read so', so)

    print2('read so.partner_id before set 1', so.partner_id)
    # # print2('read so.partner_id before set 2', so.partner_invoice_id)
    # # print2('read so.partner_id before set 3', so.partner_shipping_id)

    selection = so.get_selection('partner_id')
    print2('read so.partner_id selection:', selection)

    so.partner_id = 1
    print2('read so.partner_id after set', so.partner_id)

    print2('read so.date_order before set', so.date_order)
    so.date_order = "2021-02-10 09:35:06"
    print2('read so.date_order after set', so.date_order)

    ret = so.commit()
    print2('so commit', ret)
    print2('read so', so)


def test_write_so2():
    print2(' test start')
    model = 'sale.order'
    # model = 'ir.model'
    Model = odoo.env[model]
    print2(Model)
    context2 = {
        'allowed_company_ids': get_allowed_company_ids(),
    }

    context = {}
    context.update(Model.env.context)
    context.update(context2)

    SO = Model.with_context(context)
    print2(SO)
    id_ = 1
    view_form_xml_id = 'sale.view_order_form'
    so = SO.browse(id_, view_form_xml_id=view_form_xml_id)
    print2('read so', so)
    # p = so.partner_id
    # print2(p)

    # odoo.print_dict(so._columns)
    line = so.order_line
    print2('read line', line,  id(line._values))

    line1 = line.new()
    print2('read l2', line1)
    print2('read line', line)
    line = so.order_line
    print2('read line', line)

    # print2('read so', so._values_to_write)

    odoo.print_dict(so._values_to_write)

    # line1 = line[0]
    # print2('read line1', line1, id(line1._values))

    # print2('read line1', line1, line1._values)
    # print2('read line1', line1, line1._columns)

    # print2('read line1', so, so._values_relation)


def test_write_so():
    print2(' test start')
    model = 'sale.order'
    # model = 'ir.model'
    Model = odoo.env[model]
    print2(Model)

    context2 = {
        'allowed_company_ids': get_allowed_company_ids(),
    }

    context = {}
    context.update(Model.env.context)
    context.update(context2)

    SO = Model.with_context(context)
    print2(SO)

    # 读 so 显示
    id_ = 1

    for_edit = 1

    if for_edit:
        view_form_xml_id = 'sale.view_order_form'
        so = SO.browse(id_, view_form_xml_id=view_form_xml_id)
        # for k, v in so._columns.items():
        #     if v.type in ['one2many', 'many2many'] and k in so.field_onchange:
        #         print(v.type, k)
    else:
        so = SO.browse(id_)

    print2('read so', so)
    print2('read so.partner_id before set 1', so.partner_id)
    # print2('read so.partner_id before set 2', so.partner_invoice_id)
    # print2('read so.partner_id before set 3', so.partner_shipping_id)

    selection = so.get_selection('partner_id')
    print2('read so.partner_id selection:', selection)

    so.partner_id = 1
    # print2('read so.partner_id after set', so.partner_id)

    # print2('read so.date_order before set', so.date_order)
    # so.date_order = "2021-02-10 09:35:06"
    # print2('read so.date_order after set', so.date_order)

    so.commit()


def test_write_sol():
    print2(' test start')
    model = 'sale.order'
    # model = 'ir.model'
    Model = odoo.env[model]
    print2(Model)
    # print2(Model.env)
    context2 = {
        'allowed_company_ids': get_allowed_company_ids(),
    }

    context = {}
    context.update(Model.env.context)
    context.update(context2)

    SO = Model.with_context(context)
    print2(SO)
    # print2(SO.env)

    id_ = 1

    view_form_xml_id = 'sale.view_order_form'
    so = SO.browse(id_, view_form_xml_id=view_form_xml_id)
    print2('read so', so)

    # print2('read so', so)

    # # odoo.print_dict(so.field_onchange)

    # # # # 读 sol 显示
    print2('read 1 line', )
    line = so.order_line

    ss1 = line.get_selection('product_uom', context={
                             'product_uom_category_id': 1})

    print2('read 1 line', ss1)

    ss = so.get_selection('order_line.product_uom', context={
        'product_uom_category_id': 1})

    print2('read 1 line', ss)

    # for k, Field in line._columns.items():
    #     print(k,  getattr(Field, 'domain', False))

    # print2('line 1', line)
    # # print2('line 1', so._columns['order_line']._data)
    # # print2('line 1', line._from_record[1]._data)
    # # print2('line 1', line._from_record[0]._columns['order_line']._data)

    # # 编辑 line
    # # line0 = line[0]
    # # print2('line 1', line0)

    # # product_uom_qty = line0.product_uom_qty
    # # print2('line 1', product_uom_qty)

    # # line0.product_uom_qty = 12

    # # # # # new order line
    # print2('read 1 line new', )
    # line0 = so.order_line.new()
    # # print2('line new', line0, line0._values)
    # # print2('line new', line0, line0._values_to_write)
    # # print2('line 1', line, line._values)
    # # print2('line 1', line, line._values_to_write)

    # # print2('line 1', line0._from_record)
    # # print2('line 1', [so._columns['order_line']])

    # # print2('line 1', line0._from_record[1]._data)
    # # print2('line 1', line0._from_record[0]._columns['order_line']._data)

    # product_id = line0.product_id
    # print2('line new pid', product_id)

    # line0.product_id = 2
    # print2('line 1', product_id)

    # # print2('so', so._values,)
    # # print2('so', so._values_to_write,)

    # # line = so.order_line
    # # print2('sol all:', line)

    # line6 = so.order_line[0]
    # print2('sol line6:', line6)

    # product_uom_qty = line6.product_uom_qty
    # print2('line6', product_uom_qty)

    # line6.product_uom_qty = 18

    # print2('line6', product_uom_qty)
    # line0.product_uom_qty = 12

    # # print2('so', line0,)
    # so.commit()


def get_onchange_spec():
    model = 'res.partner.title'
    # model = 'ir.model'
    Model = odoo.env[model]
    print2(Model)

    res = Model._onchange_spec()

    print(res)

    odoo.print_dict(res)


def test2():
    # test_create_so()
    # test_write_so()
    test_write_so2()

    # test_write_sol()

    # get_onchange_spec()

    # create 时 测试  order_line
    # test_create_sol()

    # M = odoo.env['ir.sequence.date_range']
    # ids = M.search([])

    # m = M.browse(ids)

    # print(m.date_from, type(m.date_from))

    pass


test2()
