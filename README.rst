=======
OdooRPC2
=======

**OdooRPC2** is an extended Python package for **OdooRpc**.

Features supported:

1. - follow **OdooRpc**,
2. - all method in **OdooRpc** can used,
3. - some magic for create, write, onchange

How does it work? See below:

.. code-block:: python

    import odoorpc2
    odoo = odoorpc.ODOO('localhost', port=8069)
    odoo.login('db_name', 'user', 'passwd')

    model = 'sale.order'
    Model = odoo.env[model]

    company_id = 1
    context2 = {
        'allowed_company_ids': [company_id],
    }

    context = {}
    context.update(Model.env.context)
    context.update(context2)

    # sale.order model
    SO = Model.with_context(context)

    # use this xml id to create or write sale order
    view_form_xml_id = 'sale.view_order_form'

    # prepare to create a sale order
    so = SO.browse(None, view_form_xml_id=view_form_xml_id)

    # prepare to edit a sale order
    so_ids = SO.search([])
    so_id = so_ids[0] # get a so id
    so = SO.browse(so_id, view_form_xml_id=view_form_xml_id)

    # get selection for partner_id field of sale.order
    selection = so.get_selection('partner_id')

    # set partner_id
    so.partner_id = 1

    so.date_order = "2021-02-10 09:35:06"

    # order_line field of sale.order
    lines = so.order_line

    # new order line of sale.order
    line1 = so.order_line.new()
    line2 = so.order_line.new()

    # get selection for product_id field of sale.order.line
    selection = so.get_selection('order_line.product_id')

    # set field for order line
    line1.product_id = 1
    line2.product_id = 2

    # line1 and line2  all in lines
    line_ids = lines.ids

    # read other field in order_line, maybe set by onchange
    lines[0].product_uom_qty

    # read other field in sale.order, maybe set by onchange
    so.amount_total

    # commit all changed, call create for new sale.order, or write for exist sale.order
    so.commit()

See the documentation for more details and features.

# Supported Odoo server versions

`Odoo` 13
`Odoo` 14

# License

This software is made available under the `LGPL v3` license.

# Credits

## Contributors

- Master Zhang <odoowww@163.com> <winboy99@163.com>

## Maintainer

This package is maintained by the Master Zhang <odoowww@163.com> <winboy99@163.com>.

```

```
