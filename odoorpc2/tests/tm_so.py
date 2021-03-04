
from odoorpc2.tests import LoginTestCase

from odoorpc2.models import Model

from odoorpc2.fields import BaseField
from odoorpc2.env import Environment

import sys


class TestModelSO(LoginTestCase):
    def test_browse(self):
        print('run', self.__class__.__name__, sys._getframe().f_code.co_name)
        SO = self.odoo.env['sale.order']
        so_ids = SO.search([])
        so = SO.browse(so_ids)

    # def test_1(self):
    #     print('run', self.__class__.__name__, sys._getframe().f_code.co_name)
    #     SO = self.odoo.env['sale.order']
    #     view_form_xml_id = 'sale.view_order_form'
    #     so_ids = SO.search([])
    #     so = SO.browse(so_ids, view_form_xml_id)
    #     so.order_line

    # def test_field_onchange(self):
    #     print('run', self.__class__.__name__, sys._getframe().f_code.co_name)
    #     SO = self.odoo.env['sale.order']
    #     view_form_xml_id = 'sale.view_order_form'
    #     field_onchange = SO._get_field_onchange(view_form_xml_id)

    #     self.assertIn('order_line', field_onchange)
    #     self.assertEqual(field_onchange['order_line'], '1')

    #     self.assertIn('state', field_onchange)
    #     self.assertEqual(field_onchange['state'], '1')

    #     self.assertIn('name', field_onchange)
    #     self.assertEqual(field_onchange['name'], None)

    #     self.assertIn('order_line.price_unit', field_onchange)
    #     self.assertEqual(field_onchange['order_line.price_unit'], '1')

    #     self.assertIn('order_line.price_subtotal', field_onchange)
    #     self.assertEqual(field_onchange['order_line.price_subtotal'], None)

    #     # self.odoo.print_dict(field_onchange)
