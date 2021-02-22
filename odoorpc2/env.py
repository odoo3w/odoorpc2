
from odoorpc2.models import Model
from odoorpc2 import fields
from odoorpc.env import FIELDS_RESERVED

import sys


from odoorpc.env import Environment as odoorpc_Environment


class Environment(odoorpc_Environment):

    def __repr__(self):
        return "Environment2(db=%s, uid=%s, context=%s)" % (
            repr(self._db), self._uid, self._context)

    def commit(self):
        """
        never call commit in env.
        we imple commit in Model by 'write' and 'create' method 
        """
        return

    def __call__(self, context=None):
        """
        重写这个方法 是因为  Model.with_context 方法中 用到了 cls.env()
        而这里的代码: 
         env = Environment(self._odoo, self._db, self._uid, context)
         Environment 是 hard cord
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
        """ 重写这个方法 是为了 
        1. 用 odoorpc2 中 扩展的 Model 和 fields
        2. 记录 _model_id, 服务于 domain str2list
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
        if 'name' not in attrs['_columns']:
            field_data = {'type': 'text', 'string': 'Name', 'readonly': True}
            Field = fields.generate_field('name', field_data)
            attrs['_columns']['name'] = Field
            attrs['name'] = Field
        return type(cls_name, (Model,), attrs)
