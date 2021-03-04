# -*- coding: UTF-8 -*-
##############################################################################
#
#    OdooRPC
#    Copyright (C) 2020 Master Zhang <odoowww@163.com>.
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


from odoorpc2.models import Model
from odoorpc2 import fields
from odoorpc.env import FIELDS_RESERVED

import sys


from odoorpc.env import Environment as odoorpc_Environment


class Environment(odoorpc_Environment):
    """ Override odoorpc.env.Environment.
    rewrite method: commit, __call__, _create_model_class
    """

    def __repr__(self):
        return "Environment2(db=%s, uid=%s, context=%s)" % (
            repr(self._db), self._uid, self._context)

    def commit(self):
        """
        never call commit in env.
        call commit in Model by 'write' and 'create' method 
        """
        return

    def __call__(self, context=None):
        """
        Rewrite this method, because:
        This method be called in method with_context of Model Class.
        But in here, 'Environment' should be Environment in odooRpc2
        """
        # print('env call:', self)
        # print('env call:', self.__class__)
        # print('env call:', Environment)
        # print('env call:', id(self.__class__))
        # print('env call:', id(Environment))

        context = self.context if context is None else context
        # env = Environment(self._odoo, self._db, self._uid, context)
        env = self.__class__(self._odoo, self._db, self._uid, context)
        env._dirty = self._dirty
        env._registry = self._registry
        return env

    def _create_model_class(self, model):
        """
        Rewrite this method, because:
        1. 'Model' should be Model in odooRpc2
        2. 'fields' should be fields in odooRpc2
        3. new attribute of '_model_id' is used for fields_get domain string to list
        4. field name need not append if not in fields_get
        """

        cls_name = model.replace('.', '_')
        # Hack for Python 2 (no need to do this for Python 3)
        if sys.version_info[0] < 3:
            if isinstance(cls_name, unicode):
                cls_name = cls_name.encode('utf-8')
        # Retrieve server fields info and generate corresponding local fields

        attrs = {
            '_env': self,
            '_odoo': self._odoo,
            '_name': model,
            '_model_id': None,  # 用于 处理 fields 中的 domain str2list
            '_columns': {},
        }
        fields_get = self._odoo.execute(model, 'fields_get')

        # self._odoo.print_dict(fields_get, 'field_get')

        for field_name, field_data in fields_get.items():
            if field_name not in FIELDS_RESERVED:
                Field = fields.generate_field(field_name, field_data)
                attrs['_columns'][field_name] = Field
                attrs[field_name] = Field

        # Case where no field 'name' exists, we generate one (which will be
        # in readonly mode) in purpose to be filled with the 'name_get' method

        # this is a bug in odoorpc
        # 'name' field not in feilds_get, so browse raise error
        # 'display_name' field can be used for 'name_get' method
        # if 'name' not in attrs['_columns']:
        #     field_data = {'type': 'text', 'string': 'Name', 'readonly': True}
        #     Field = fields.generate_field('name', field_data)
        #     attrs['_columns']['name'] = Field
        #     attrs['name'] = Field
        return type(cls_name, (Model,), attrs)
