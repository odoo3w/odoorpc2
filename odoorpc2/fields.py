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

""" Inherited form odoorpc.fields.

Override `__set__` method to call `onchange` method for odoo
Rewrite `One2many` Class to prepare values for `create` or `write`

"""


from odoorpc.models import IncrementalRecords
from odoorpc2.models import Model
from odoorpc2.models import is_virtual_id


from odoorpc import fields

from odoorpc.fields import BaseField as odoorpc_BaseField

from odoorpc.fields import Binary as odoorpc_Binary
from odoorpc.fields import Boolean as odoorpc_Boolean
from odoorpc.fields import Char as odoorpc_Char
from odoorpc.fields import Date as odoorpc_Date
from odoorpc.fields import Datetime as odoorpc_Datetime
from odoorpc.fields import Float as odoorpc_Float

from odoorpc.fields import Html as odoorpc_Html
from odoorpc.fields import Integer as odoorpc_Integer
from odoorpc.fields import Many2many as odoorpc_Many2many
from odoorpc.fields import Many2one as odoorpc_Many2one
from odoorpc.fields import One2many as odoorpc_One2many
from odoorpc.fields import Reference as odoorpc_Reference
from odoorpc.fields import Selection as odoorpc_Selection
from odoorpc.fields import Text as odoorpc_Text
from odoorpc.fields import Unknown as odoorpc_Unknown


def merge_tuples_one(old_tuples, tuple_in):
    if tuple_in[0] in [6, 5]:
        # for 2m2, new=6,5, old=any
        return [tuple_in]

    to_append = tuple_in
    newval = tuple_in

    temp = []
    for oldval in old_tuples:
        if oldval[0] in [6, 5]:
            # 1st, new=4,3,2,1,0, old=6,5
            temp.append(oldval)
            to_append = newval
        elif newval[1] != oldval[1]:
            # 2nd, new=4,3,2,1,0, old=4,3,2,1,0, id not equ
            temp.append(oldval)
            # to_append = newval

        # id equ.
        elif oldval[0] == 0:
            if newval[0] == 0:
                # 3rd, new=0, old=0, id equ  # new update
                to_append = newval
            elif newval[0] in [2, 3]:
                # 4th, new line then delete, # this a extend for odoo
                to_append = None
            else:
                # 5th, never goto here
                to_append = None
        elif oldval[0] in [1, 4]:
            if newval[0] in (1, 2, 3):
                # 6th, old line , then edit or del
                to_append = newval
            elif newval[0] == 4:
                # 7th, few goto here. old then add.
                to_append = oldval
            else:
                # 8th, never goto here. old then ...
                to_append = None

        elif oldval[0] in [2, 3]:
            if newval[0] == 4:
                # 9th, del then add
                to_append = newval
            else:
                # 10th, never goto here. old=2,3 new=1,2,3. del then del, edit
                to_append = oldval
        else:  # never goto here
            # to_append = newval
            pass

    if to_append:
        temp.append(to_append)

    return temp


def merge_tuples(old_tuples, new_tuples):
    ret = old_tuples[:]
    for tuple_in in new_tuples:
        ret = merge_tuples_one(ret, tuple_in)

    return ret


# def odoo_tuple_in(iterable):
#     """Return `True` if `iterable` contains an expected tuple like
#     ``(6, 0, IDS)`` (and so on).

#         >>> odoo_tuple_in([0, 1, 2])        # Simple list
#         False
#         >>> odoo_tuple_in([(6, 0, [42])])   # List of tuples
#         True
#         >>> odoo_tuple_in([[1, 42]])        # List of lists
#         True
#     """
#     if not iterable:
#         return False

#     def is_odoo_tuple(elt):
#         """Return `True` if `elt` is a Odoo special tuple."""
#         try:
#             return elt[:1][0] in [1, 2, 3, 4, 5] \
#                 or elt[:2] in [(6, 0), [6, 0], (0, 0), [0, 0]]
#         except (TypeError, IndexError):
#             return False
#     return any(is_odoo_tuple(elt) for elt in iterable)


# def tuples2ids(tuples, ids):
#     """Update `ids` according to `tuples`, e.g. (3, 0, X), (4, 0, X)..."""
#     for value in tuples:
#         if value[0] == 6 and value[2]:
#             ids = value[2]
#         elif value[0] == 5:
#             ids[:] = []
#         elif value[0] in [4, 0, 1] and value[1] and value[1] not in ids:
#             ids.append(value[1])
#         elif value[0] in [3, 2] and value[1] and value[1] in ids:
#             ids.remove(value[1])

#     return ids


# def records2ids(iterable):
#     """Replace records contained in `iterable` with their corresponding IDs:

#         >>> groups = list(odoo.env.user.groups_id)
#         >>> records2ids(groups)
#         [1, 2, 3, 14, 17, 18, 19, 7, 8, 9, 5, 20, 21, 22, 23]
#     """
#     def record2id(elt):
#         """If `elt` is a record, return its ID."""
#         if isinstance(elt, Model):
#             return elt.id
#         return elt
#     return [record2id(elt) for elt in iterable]


class BaseField(odoorpc_BaseField):
    """Field which all other fields inherit.
    Manage common metadata.
    """

    def _get_readonly(self, instance):
        state = None
        if 'state' in instance._columns:
            state = instance._values['state'][instance.id]
            if instance.id in instance._values_to_write['state']:
                state = instance._values_to_write['state'][instance.id]

        if state and self.states and self.states.get(state):
            readonly2 = dict(self.states.get(state))
            if 'readonly' in readonly2:
                return readonly2['readonly']

        return self.readonly

    def get_for_create(self, instance):
        # 被  instance._get_values_for_create 调用

        columns = [fld for fld in instance.field_onchange if len(
            fld.split('.')) == 1]

        if self.name not in columns:
            return None

        if self._get_readonly(instance):
            return None

        if instance.id not in instance._values[self.name]:
            return None

        # 从 _values 中获取默认值
        value = instance._values[self.name][instance.id]

        # 从 _values_to_write 中获取编辑过的结果
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]

        return value

    def get_for_write(self, instance):
        # 被  instance._get_values_for_write 调用

        # 未被修改或只读字段, 无需提交. 用 None 表示
        # odoo 返回的值 没有 None. 空值时 是 False

        if self._get_readonly(instance):
            return None

        if instance.id not in instance._values_to_write[self.name]:
            return None

        return instance._values_to_write[self.name][instance.id]

    def get_for_onchange(self, instance, **kwargs):
        # 仅被 instance._get_values_for_onchange 调用
        value = instance._values[self.name].get(instance.id)
        if instance.id in instance._values_to_write[self.name]:
            value = instance._values_to_write[self.name][instance.id]
        return value

    def __set__(self, instance, value):
        """Each time a record is modified,
        DONT marked as dirty in the environment.
        call `onchange` method for odoo
        """
        # print('base set', self, instance, value)

        if not instance.field_onchange:
            return super().__set__(instance, value)

        instance.trigger_onchange(self.name)

        # 这里不调 super().__set__,
        # 在编辑页面下, 不写 instance.env.dirty
        #
        return

    def commit(self, instance):
        # only a skeleton, to be overrid for o2m
        pass


class Binary(odoorpc_Binary, BaseField):
    """Equivalent of the `fields.Binary` class."""


class Boolean(odoorpc_Boolean, BaseField):
    """Equivalent of the `fields.Boolean` class."""


class Char(odoorpc_Char, BaseField):
    """Equivalent of the `fields.Char` class."""


class Date(odoorpc_Date, BaseField):
    """Represent the OpenObject 'fields.data'"""


class Datetime(odoorpc_Datetime, BaseField):
    """Represent the OpenObject 'fields.datetime'"""


class Float(odoorpc_Float, BaseField):
    """Equivalent of the `fields.Float` class."""


class Monetary(Float):
    """Equivalent of the `fields.Float` Monetary."""


class Integer(odoorpc_Integer, BaseField):
    """Equivalent of the `fields.Integer` class."""


class Selection(odoorpc_Selection, BaseField):
    """Represent the OpenObject 'fields.selection'"""


class Many2many(odoorpc_Many2many, BaseField):
    """Represent the OpenObject 'fields.many2many'"""

    def get_for_onchange(self, instance, **kwargs):
        # 仅被 instance._get_values_for_onchange 调用
        # TBD 这个未认真测试过
        # in _values:  (6, 0, ids)
        # in _values_to_write:  (5,), (4,id), (3,id)
        tuples = []
        ids_old = instance._values[self.name][instance.id] or []
        tuples.append((6, 0, ids_old))

        if instance.id in instance._values_to_write[self.name]:
            # 处理  修改过的
            for tuple_ in instance._values_to_write[self.name][instance.id]:
                tuples.append(tuple_)
        return tuples


class Many2one(odoorpc_Many2one, BaseField):
    """Represent the OpenObject 'fields.many2one'"""


class One2many(odoorpc_One2many, BaseField):
    """Represent the OpenObject 'fields.one2many'"""

    # `__get__` function extend for edit
    # `_values` and `_values_to_write` of relation Model is located in here

    def __init__(self, name, data):
        # 整理 onchange 参数 values 时, 需要 relation_field
        # 编辑查询时, 使用 storage:record 暂存结果
        # 编辑查询时, 这里预定义 storage: _values _values_to_write
        # 这样任何 新增/切片 等操作, 操作结果都指向这里

        super(One2many, self).__init__(name, data)
        self.relation_field = 'relation_field' in data and data['relation_field'] or False

    def _init_storage(self, instance):
        if not hasattr(instance, '_values_relation'):
            instance._values_relation = {}

        if instance._values_relation.get(self.name) is None:
            instance._values_relation[self.name] = {}
            storage = instance._values_relation[self.name]
            storage['records'] = None
            storage['_values'] = {}
            storage['_values_to_write'] = {}

            Relation = instance.env[self.relation]
            for field in Relation._columns:
                storage['_values'][field] = {}
                storage['_values_to_write'][field] = {}

    def _get_storage_records(self, instance):
        if hasattr(instance, '_values_relation'):
            if instance._values_relation.get(self.name):
                storage = instance._values_relation[self.name]
                return storage.get('records')

        return None

    def _get_storage(self, instance):
        # print('_get_storage ', self.name, instance)
        self._init_storage(instance)
        storage = instance._values_relation[self.name]
        # print('_get_storage', storage)

        return storage

    def __get__(self, instance, owner):
        """Return a recordset."""
        # print('One2many get:', self, instance, owner)

        # 普通查询
        if not instance.field_onchange:
            return super().__get__(instance, owner)

        storage = self._get_storage(instance)

        if storage.get('records'):
            # # 编辑查询, 已经读取过了
            return storage['records']

        # # 编辑查询, 需要初始化, 并且 暂存
        # super 里 用到了 tuples2ids? 是否需要重写?
        relation = super().__get__(instance, owner)
        storage['records'] = relation
        return relation

    def _update_relation(self, instance, o2m_id, values):
        # 仅仅 被 instance._update_parent 调用
        # TBD check

        op = (not is_virtual_id(o2m_id)) and 1 or 0
        new_value = [(op, o2m_id, values)]
        old_value = instance._values_to_write[self.name].get(instance.id, [])
        values_to_write = merge_tuples(old_value, new_value)
        instance._values_to_write[self.name][instance.id] = values_to_write

        relation = self._get_storage_records(instance)

        if relation and o2m_id not in relation._ids:
            relation._ids.append(o2m_id)

    def get_for_onchange(self, instance, for_parent=None):
        # 仅被 instance._get_values_for_onchange 调用

        value = instance._values[self.name][instance.id] or []

        value = [(4, id_, False) for id_ in value]

        if instance.id in instance._values_to_write[self.name]:
            value_to_write = instance._values_to_write[self.name][instance.id]
            # TBD 处理  修改过的
            value = merge_tuples(value, value_to_write)

        # sol.onchange(values, ...)
        # values = {
        #     ...,
        #     order_id: {
        #         ...
        #         order_line: {
        #             ...
        #         }
        #     }
        # }
        # 这种情况下, 组织 sol 的 onchang values时,
        # 需要嵌套 组织 order_id, 此时 传参数 for_parent=True
        # 在读取 order_line时, 进到这个函数中.

        if for_parent:
            return value

        relation = self._get_storage_records(instance)
        if not relation:
            return value

        value2 = []
        for tup in value:
            if tup[0] not in [0, 1]:
                value2.append(tup)
                continue

            # tup_op, tup_id, tup_vals = tup
            relation2 = relation[relation.ids.index(tup[1])]
            tup_vals2 = relation2._get_values_for_onchange(for_relation=True)
            new_tup = (tup[0], tup[1], tup_vals2)
            value2.append(new_tup)

        return value2

    def _get_for_CU(self, instance, value):
        if value is None:
            return value

        relation = self._get_storage_records(instance)
        if not relation:
            return value

        value2 = []
        for tup in value:
            if tup[0] not in [0, 1]:
                value2.append(tup)
                continue

            # tup_op, tup_id, tup_vals = tup
            relation2 = relation[relation.ids.index(tup[1])]

            # 递归处理, o2m
            fn = tup[0] and relation2._get_values_for_write or relation2._get_values_for_create
            tup_vals2 = fn()
            new_tup = (tup[0], tup[1], tup_vals2)
            value2.append(new_tup)

        return value2

    def get_for_create(self, instance):
        # 尚未测试过
        # print('get_for_create', self.name,  instance)
        value = super().get_for_create(instance)
        return self._get_for_CU(instance, value)

    def get_for_write(self, instance):
        # print('get_for_write', self.name,  instance)
        value = super().get_for_write(instance)
        return self._get_for_CU(instance, value)

    def commit(self, instance):
        # if instance.id in instance._values_to_write[self.name]:
        #     instance._values_to_write[self.name].pop(instance.id)
        #     instance._values[self.name][instance.id] = None

        def _get_storage_sync():
            if instance._values_relation:
                if instance._values_relation.get(self.name):
                    storage = instance._values_relation[self.name]
                    return storage

            return None

        storage = _get_storage_sync()
        if not storage.records:
            return

        records = storage.records
        for field in records._values:
            for o2m_id in records._values[field]:
                del records._values[field][o2m_id]

        for field in records._values_to_write:
            for o2m_id in records._values_to_write[field]:
                del records._values_to_write[field][o2m_id]

        storage.records = None


class Reference(odoorpc_Reference, BaseField):
    """Represent the OpenObject 'fields.reference'."""

    # few model have `Reference` field
    # if used, must be test here


class Text(odoorpc_Text, BaseField):
    """Equivalent of the `fields.Text` class."""


class Html(odoorpc_Html, BaseField):
    """Equivalent of the `fields.Html` class."""


class Unknown(odoorpc_Unknown, BaseField):
    """Represent an unknown field. This should not happen but this kind of
    field only exists to avoid a blocking situation from a RPC point of view.
    """


TYPES_TO_FIELDS = {
    'binary': Binary,
    'boolean': Boolean,
    'char': Char,
    'date': Date,
    'datetime': Datetime,
    'float': Float,
    'html': Html,
    'integer': Integer,
    'many2many': Many2many,
    'many2one': Many2one,
    'one2many': One2many,
    'reference': Reference,
    'selection': Selection,
    'text': Text,
    'monetary': Monetary,
}


def generate_field(name, data):
    assert 'type' in data
    field = TYPES_TO_FIELDS.get(data['type'], Unknown)(name, data)
    return field
