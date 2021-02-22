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


def merge_tuples(old_tuples, new_tuples):
    ret = old_tuples[:]
    for newval in new_tuples:
        temp = []
        to_append = newval

        for oldval in ret:
            if newval[0] in [6, 5]:
                # new=6,5, old=any
                to_append = newval
                break
            elif oldval[0] in [6, 5]:
                # new=4,3,2,1,0, old=6,5
                temp.append(oldval)
                to_append = newval
            elif newval[1] != oldval[1]:
                # new=4,3,2,1,0, old=4,3,2,1, id not equ
                temp.append(oldval)
                # to_append = newval
            elif oldval[0] == 0 and newval[0] == 0:
                # new=4,3,2,1,0, old=4,3,2,1, id equ
                # new update
                to_append = newval
            elif oldval[0] == 0 and newval[0] in [2, 3]:
                # new line then delete
                # this a extend for odoo
                to_append = None
            elif oldval[0] == 0 and newval[0] not in [0, 2, 3]:
                # never goto here
                to_append = None
            elif oldval[0] in [1, 4] and newval[0] in (1, 2, 3):
                # old line , then edit or del
                to_append = newval
            elif oldval[0] in [1, 4] and newval[0] == 4:
                # 几乎不会出现
                # old then add
                to_append = oldval
            elif oldval[0] in [1, 4] and newval[0] not in (1, 2, 3, 4):
                # never goto here
                # old then ...
                to_append = None
            elif oldval[0] in [2, 3] and newval[0] == 4:
                # del then add
                to_append = newval
            elif oldval[0] in [2, 3] and newval[0]in (2, 3):
                # never goto here
                # del then del
                to_append = oldval
            elif oldval[0] in [2, 3] and newval[0] == 1:
                # never goto here
                # del then edit
                to_append = oldval
            elif oldval[0] in [2, 3] and newval[0] not in (1, 2, 3, 4):
                # never goto here
                # del then ...
                to_append = oldval
            else:  # never goto here
                # to_append = newval
                pass

        if to_append:
            temp.append(to_append)
        ret = temp

    return ret


def odoo_tuple_in(iterable):
    """Return `True` if `iterable` contains an expected tuple like
    ``(6, 0, IDS)`` (and so on).

        >>> odoo_tuple_in([0, 1, 2])        # Simple list
        False
        >>> odoo_tuple_in([(6, 0, [42])])   # List of tuples
        True
        >>> odoo_tuple_in([[1, 42]])        # List of lists
        True
    """
    if not iterable:
        return False

    def is_odoo_tuple(elt):
        """Return `True` if `elt` is a Odoo special tuple."""
        try:
            return elt[:1][0] in [1, 2, 3, 4, 5] \
                or elt[:2] in [(6, 0), [6, 0], (0, 0), [0, 0]]
        except (TypeError, IndexError):
            return False
    return any(is_odoo_tuple(elt) for elt in iterable)


def tuples2ids(tuples, ids):
    """Update `ids` according to `tuples`, e.g. (3, 0, X), (4, 0, X)..."""
    for value in tuples:
        if value[0] == 6 and value[2]:
            ids = value[2]
        elif value[0] == 5:
            ids[:] = []
        elif value[0] in [4, 0, 1] and value[1] and value[1] not in ids:
            ids.append(value[1])
        elif value[0] in [3, 2] and value[1] and value[1] in ids:
            ids.remove(value[1])

    return ids


def records2ids(iterable):
    """Replace records contained in `iterable` with their corresponding IDs:

        >>> groups = list(odoo.env.user.groups_id)
        >>> records2ids(groups)
        [1, 2, 3, 14, 17, 18, 19, 7, 8, 9, 5, 20, 21, 22, 23]
    """
    def record2id(elt):
        """If `elt` is a record, return its ID."""
        if isinstance(elt, Model):
            return elt.id
        return elt
    return [record2id(elt) for elt in iterable]


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

        def _fn():
            if not state:
                return self.readonly
            if not self.states:
                return self.readonly
            readonly2 = self.states.get(state)
            if not readonly2:
                return self.readonly
            readonly2 = dict(readonly2)
            if 'readonly' not in readonly2:
                return self.readonly
            return readonly2['readonly']
        ret = _fn()

        # readonly = self.readonly
        # states = self.states
        # print('_get_readonly',  ret, self.name, state,  readonly, states)

        return ret

    def _get_for_create(self, instance):
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

    def _get_for_write(self, instance):
        # 被  instance._get_values_for_write 调用

        # 未被修改或只读字段, 无需提交. 用 None 表示
        # odoo 返回的值 没有 None. 空值时 是 False

        if instance.id not in instance._values_to_write[self.name]:
            return None

        if self._get_readonly(instance):
            return None

        return instance._values_to_write[self.name][instance.id]

    def _get_for_onchange(self, instance, **kwargs):
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

        if instance._from_record:
            instance._update_parent()

        instance._trigger_onchange(self.name)

        if instance._from_record:
            parent = instance._from_record[0]
            field = instance._from_record[1]
            # print('base set 3', parent, field)

            if parent.field_onchange.get('%s.%s' % (field.name, self.name)):
                parent._trigger_onchange(field.name)

        # 这里不调 super().__set__,
        # 在编辑页面下, 不写 instance.env.dirty
        #
        return


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

    def _get_for_onchange(self, instance, **kwargs):
        # 仅被 instance._get_values_for_onchange 调用

        # TBD 这个未认真测试过

        ids = instance._values[self.name][instance.id] or []
        # print('_get_for_onchange', value_dict)
        if instance.id in instance._values_to_write[self.name]:
            values = instance._values_to_write[self.name][instance.id]
            # 处理  修改过的
            ids = tuples2ids(values, ids or [])

        value = [(6, 0, ids)]

        return value


class Many2one(odoorpc_Many2one, BaseField):
    """Represent the OpenObject 'fields.many2one'"""


class One2many(odoorpc_One2many, BaseField):
    """Represent the OpenObject 'fields.one2many'"""

    # `__get__` function extend for edit
    # `_values` and `_values_to_write` of relation Model is located in here

    def __init__(self, name, data):
        # 整理 onchange 参数 values 时, 需要 relation_field
        # 编辑查询时, 使用 _data 暂存结果
        # 编辑查询时, 这里预定义 _values _values_to_write
        # 这样任何 新增/切片 等操作, 操作结果都指向这里

        super(One2many, self).__init__(name, data)
        self.relation_field = 'relation_field' in data and data['relation_field'] or False
        self._data = {}
        self._values = {}
        self._values_to_write = {}

    def __get__(self, instance, owner):
        """Return a recordset."""
        # print('One2many get:', self, instance, owner)

        # 普通查询
        if not instance.field_onchange:
            return super().__get__(instance, owner)

        # 编辑查询, 已经读取过了
        if instance.id in self._data:
            return self._data[instance.id]

        # 编辑查询, 需要初始化, 并且 暂存
        relation = super().__get__(instance, owner)
        self._data[instance.id] = relation
        return relation

    def _get_for_CU(self, instance, value):
        if value is None:
            return value

        if instance.id not in self._data:
            return value

        relation = self._data[instance.id]

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

    def _get_for_create(self, instance):
        # 尚未测试过
        # print('_get_for_create', self.name,  instance)
        value = super()._get_for_create(instance)
        return self._get_for_CU(instance, value)

    def _get_for_write(self, instance):
        # print('_get_for_write', self.name,  instance)
        value = super()._get_for_write(instance)
        return self._get_for_CU(instance, value)

    def _get_for_onchange(self, instance, for_parent=None):
        # 仅被 instance._get_values_for_onchange 调用

        print('_get_for_onchange', self.name,  instance, for_parent)

        value = instance._values[self.name][instance.id] or []

        value = [(4, id_, False) for id_ in value]

        # print('_get_for_onchange', value_dict)
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

        if instance.id not in self._data:
            return value

        relation = self._data[instance.id]

        # print('_get_for_onchange  relation 2', relation)
        # print('_get_for_onchange 3', value)

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

        # print('_get_for_onchange 4', value2)

        return value2

    def _update_relation(self, instance, o2m_id, values):
        # 仅仅 被 instance._update_parent 调用

        op = (not is_virtual_id(o2m_id)) and 1 or 0
        new_value = [(op, o2m_id, values)]
        old_value = instance._values_to_write[self.name].get(instance.id, [])
        values_to_write = merge_tuples(old_value, new_value)
        instance._values_to_write[self.name][instance.id] = values_to_write

        if instance.id in self._data:
            relation = self._data[instance.id]
            if o2m_id not in relation._ids:
                relation._ids.append(o2m_id)


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
