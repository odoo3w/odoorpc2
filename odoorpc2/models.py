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


from lxml import etree


from odoorpc.models import Model as odoorpc_Model
from odoorpc.models import IncrementalRecords
from odoorpc.models import _normalize_ids


from odoorpc import error


def print2(*args):
    print(' ............. in model ........... :')
    print(' ....:', *args)


def is_virtual_id(id_):
    return isinstance(id_, str) and id_[:8] == 'virtual_'


class Model(odoorpc_Model):
    """
    1. append some function to call create, write, onchange method for odoo
    2 new or update one2many field value

    some changed:
     1. `get_selection` new method for `many2one` or `many2many` field selection
     2. `browse` method is extend for prepare values for `create`
     3. `new', a new method for `one2many` field
     4. `commit`, a new method to call `create` or `write`
     5. some other function for `onchange` or `one2many` field

    """

    _field_onchanges = {}

    def __init__(self):
        super().__init__()

        # a new attribute for onchange method
        self._field_onchange = None  # 编辑页面用

    @property
    def field_onchange(self):
        # a new attribute for onchange method
        return self._field_onchange

    def __repr__(self):
        return "Recordset2(%r, %s)" % (self._name, self.ids)

    """
    SO = odoo.env[model]
    so = SO.browse(id)
    sol = so.order_line
    new_line = sol.new()
    
    1. read: browse(ids),                    call super._browse
    2. iter: _browse(id_ iterated)           call _browse
    2. new:  browse(None, view_form_xml_id), call _browse2
    3. edit: browse(id_,  view_form_xml_id), call _browse2
    5. m2o:  _browse(ids, form_record),      call super._browse
    5. m2m:  _browse(ids, form_record),      call super._browse
    5. o2m.read:  _browse(ids, form_record), call super._browse
    5. o2m.edit:  _browse(ids, form_record), call _browse2
    5. o2m.new:   sol.new(),                 call _browse2
    5. o2m.iter:  _browse(ids, iterated),    call _browse

    """

    def new(self):
        """
        # o2m 字段, 新增时 调用 new 方法

        # so = odoo.env['sale.order'].browse(1)
        # sol = so.order_line
        # a_new_sol = sol.new()

        # 考虑过其他办法, 待议. 如:
        # a_new_sol = sol + None
        # a_new_sol = +sol
        # a_new_sol = sol.browse(None)
        """

        # print('new ------', self)
        if not self._from_record:
            return None

        env = self.env
        records = self.__class__._browse2(
            env, None, from_record=self._from_record)

        return records

    @classmethod
    def browse(cls, ids, view_form_xml_id=None):
        # 扩展编辑使用该方法, 新增 参数 view_form_xml_id
        # view_form_xml_id:
        #   None: 普通的 read 纯显示用
        #   dot 分割的: module_name.view_from_xml_name:
        #       编辑 读取用, 使用 view_form_xml_id 中的字段
        #   单字符串: 编辑 读取用, 使用 默认字段
        #

        if not view_form_xml_id:
            return super().browse(ids)

        return cls._browse2(cls.env, ids, view_form_xml_id=view_form_xml_id)

    @classmethod
    def _browse(cls, env, ids, from_record=None, iterated=None):
        # 重写这个方法:
        # 1. 补充切片后, 若是 编辑页面切片, 需要额外设置
        # 2. o2m字段, 通过 from_record 进来, 如果是编辑, 单独处理

        # print('_browse', cls, ids, from_record)

        if from_record:
            parent = from_record[0]
            field = from_record[1]
            if parent.field_onchange and field.type == 'one2many':
                return cls._browse2(env, ids, from_record=from_record)
                # return cls._browse_for_edit_from_record222(env, ids, from_record)

        records = super()._browse(env, ids, from_record=from_record, iterated=iterated)

        if iterated:
            # 切片后的  需要 _from_record, 触发 parent.onchange
            records._from_record = iterated._from_record
            records._field_onchange = iterated._field_onchange

        return records

    @classmethod
    def _browse2(cls, env, ids, view_form_xml_id=None, from_record=None):
        # _browse_edit_or_new, _browse_for_edit_from_record222
        # 1. browse for edit,
        # 2. browse for new,
        # 3. from_record and from_record[0].field_onchange is set and field.type == one2many
        # 4. this is all for edit

        if not view_form_xml_id:
            if not from_record:
                raise error.InternalError(
                    "No view_form_xml_id and No from_record")
            elif not from_record[0].field_onchange:
                raise error.InternalError(
                    "No from_record[0].field_onchange")
            elif from_record[1].type != 'one2many':
                raise error.InternalError(
                    "from_record.field is NOT one2many")

        records = cls()
        records._env_local = env

        ids2 = ids

        if from_record and not ids:
            # o2m, new a record
            ids2 = cls._odoo._get_virtual_id()

        records._ids = _normalize_ids(ids2)

        records._from_record = from_record
        records._field_onchange = cls._get_field_onchange(
            view_form_xml_id, from_record=from_record)

        def check_is_o2m_edit():
            if from_record:
                parent = from_record[0]
                field = from_record[1]
                if parent.field_onchange and field.type == 'one2many':
                    return True
            return False

        is_o2m_edit = check_is_o2m_edit()

        if is_o2m_edit:
            parent = from_record[0]
            field = from_record[1]
            storage = field._get_storage(parent)
            records._values = storage['_values']
            records._values_to_write = storage['_values_to_write']
        else:
            records._values = {}
            records._values_to_write = {}
            for field in cls._columns:
                records._values[field] = {}
                records._values_to_write[field] = {}

        if view_form_xml_id and records.ids:  # for main page edit
            records._init_values_for_edit()
            return records

        elif view_form_xml_id:  # for main page edit
            records._init_values_for_new()
            return records
        elif not is_o2m_edit:  # for read
            # never goto here.
            records._init_values()
            return records

        elif is_o2m_edit and not ids:  # for o2m new
            records._init_values_for_new()
            return records

        elif is_o2m_edit:  # for o2m edit
            # # ids 中 有 虚拟字段 需要处理
            # # print('_browse_for_edit_from_record222', records.ids)
            # # 1 过滤掉 其中的 虚拟id, 其余的id 刷新数据 _values
            # # 2 从 parent 中 补充虚拟id 的 刷新数据 _values, _values_to_write

            virtual_ids = [
                id_ for id_ in records.ids if is_virtual_id(id_)]
            real_ids = [
                id_ for id_ in records.ids if not is_virtual_id(id_)]

            records._init_values_for_edit(real_ids)
            records._init_values_for_virtual(virtual_ids)
            records._init_values_to_write_for_edit()
            return records
        else:  # never goto here
            raise error.InternalError(
                "No view_form_xml_id and No from_record")

        return records

    @classmethod
    def _get_default(cls, col):
        meta = cls._columns[col]
        if meta.type == 'many2many':
            return []
        elif meta.type == 'one2many':
            return []
        elif meta.type in ['float', 'integer', 'monetary']:
            return 0
        elif meta.type in ['text', 'html']:
            return ''

        return False

    def _init_values_for_new(self, context=None):
        # 主页面新增, 或者 o2m 字段新增
        # print('_init_values_for_new1111')
        for fld in self._values:
            self._values[fld][self.id] = self._get_default(fld)

        # print(self._values)
        onchange = self._onchange2({}, [], self.field_onchange)
        print2('_init_values_for_new 3 ,', onchange)
        self._after_onchange(onchange)

    def _init_values_for_edit(self, partial_ids=None, context=None):
        # 1. 主页面 编辑; 2. o2m edit; 3 create write commit 之后, 是否 重新read from odoo
        # 重写这个方法  因为
        # 1. relation 第一次 也需要 读取 过来. 这样 在 onchange 时, 才能取值
        # 2. 只读取部分ids 的值, 另外的 id 可能是虚拟的

        if context is None:
            context = self.env.context

        # Get basic fields (no relational ones)
        basic_fields = []
        # for field_name in columns:
        #     field = self._columns[field_name]
        #     if not getattr(field, 'relation', False):
        #         basic_fields.append(field_name)

        basic_fields = [col for col in self._columns]

        if partial_ids is None:
            ids = self.ids
        else:
            ids = partial_ids

        # Fetch values from the server
        if ids:
            rows = self.__class__.read(
                ids, basic_fields, context=context, load='_classic_write')
            ids_fetched = set()
            for row in rows:
                ids_fetched.add(row['id'])
                for field_name in row:
                    if field_name == 'id':
                        continue
                    self._values[field_name][row['id']] = row[field_name]

            ids_in_error = set(ids) - ids_fetched
            if ids_in_error:
                raise ValueError(
                    "There is no '{model}' record with IDs {ids}.".format(
                        model=self._name, ids=list(ids_in_error)))
        # No ID: fields filled with default values
        else:
            pass
            # default_get = self.__class__.default_get(
            #     list(self._columns), context=context)
            # for field_name in self._columns:
            #     self._values[field_name][None] = default_get.get(
            #         field_name, False)

    def _init_values_to_write_for_edit(self):
        parent = self._from_record[0]
        field = self._from_record[1]

        tuples = parent._values_to_write[field.name].get(parent.id, [])
        # print('_init_values_for_virtual22 wr', tuples)

        values_dict = dict((tup[1], tup[2])
                           for tup in tuples if tup[0] in [0, 1])

        for vid in self.ids:
            vals = values_dict.get(vid, {})
            for fld in self._values:
                if fld in vals:
                    self._values_to_write[fld][vid] = vals[fld]

    def _init_values_for_virtual(self, virtual_ids):
        for vid in virtual_ids:
            for fld in self._values:
                self._values[fld][vid] = self._get_default(fld)

    def _get_values_for_onchange(self, for_parent=None, for_relation=None):
        # 被 _trigger_onchange 调用, 组织 自己 及 parent 的 values
        # 被 _default_get_onchange 调用, 组织 parent 的 values

        print('_get_values_for_onchange 0,', self, for_parent)
        # print('_get_values_for_onchange _values,', self._values)
        # print('_get_values_for_onchange _values_to_write,', self._values_to_write)

        columns = [fld for fld in self.field_onchange if len(
            fld.split('.')) == 1]

        vals = dict(
            (fld, self._columns[fld]._get_for_onchange(
                self, for_parent=for_parent))
            for fld in columns)

        def is_to_append():
            # TBD 什么情况下 补充 id
            if not self.id:
                # 新增时没有 id
                return False
            if for_relation:
                # TBD o2m 编辑 时 需要 处理
                # 嵌套的没有 o2m 没有 id
                return False

            # 编辑时有 id
            return True

        if is_to_append():
            return dict({'id': self.id}, **vals)
        else:
            return vals

    def _trigger_onchange(self, field_name):
        print('_trigger_onchange 1,', self, field_name)
        # print('_trigger_onchange ,', self.field_onchange.get(field_name))
        # print('_trigger_onchange ,', self._values)

        if not self.field_onchange:
            return

        if self._from_record:
            self._update_parent()

        if field_name and not self.field_onchange.get(field_name):
            return

        values = self._get_values_for_onchange()

        if self._from_record:
            parent = self._from_record[0]
            field = self._from_record[1]

            # field.relation_field
            print(' _trigger_onchange,parent, field.relation_field',
                  parent, field.relation_field)
            parent_vals = parent._get_values_for_onchange(for_parent=True)
            # print(' _trigger_onchange parent_vals', parent_vals)
            # self._odoo.print_dict(
            #     parent_vals, '_trigger_onchange, parent_vals')
            values.update({
                field.relation_field: parent_vals
            })

        # self._odoo.print_dict(values, '_trigger_onchange, values')

        onchange = self._onchange2(values, field_name, self.field_onchange)
        print('_trigger_onchange 3 ,', onchange)
        self._after_onchange(onchange)

        if self._from_record:
            parent = self._from_record[0]
            field = self._from_record[1]
            # print('base set 3', parent, field)

            if parent.field_onchange.get('%s.%s' % (field.name, field_name)):
                parent._trigger_onchange(field.name)

        return

    def _after_onchange(self, onchange):

        onchange_domain = onchange.get('domain', {})
        # TBD domain set
        onchange_value = onchange['value'] or {}

        print('_after_onchange ,', onchange_value)

        for fld, val in onchange_value.items():
            meta = self._columns[fld]

            val2 = val
            if meta.type == 'many2one':
                val2 = val and val[0] or False

            self._values_to_write[fld][self.id] = val2

        if self._from_record:
            print('222_after_onchange ')
            self._update_parent()

        # print('_after_onchange  ok ,', )

    def _update_parent(self):
        # 1. 被 _after_onchange 调用
        # 2. 主动编辑 某字段后, 也调用

        if not self._from_record:
            return

        parent = self._from_record[0]
        field = self._from_record[1]
        # print('base set 3', parent, field)

        values = {}
        for fld in self._values_to_write:
            if self.id in self._values_to_write[fld]:
                values[fld] = self._values_to_write[fld][self.id]

        parent.__class__.__dict__[field.name]._update_relation(
            parent, self.id, values)

    def _get_values_for_create(self):
        # print('_get_values_for_create', self)
        vals = {}
        for fld in self._values:
            value = self._columns[fld].get_for_create(self)
            if value is None:
                continue

            vals[fld] = value

        return vals

    def _get_values_for_write(self):
        # 组织  write 方法的  vals 数据
        # 涉及到 o2m 字段, 会递归调用

        # print('_get_values_for_write', self)
        vals = {}
        for fld in self._values_to_write:
            value = self._columns[fld].get_for_write(self)
            if value is None:
                continue

            vals[fld] = value

        return vals

    def _commit_create(self, follow_read=None):
        vals = self._get_values_for_create()
        # # print('commit', vals)
        # self._odoo.print_dict(vals, 'commit')

        id_ = self.__class__.create(vals)
        if not id_:
            return id_

        for fld in self._values:
            del self._values[fld][None]
            if None in self._values_to_write[fld]:
                del self._values_to_write[fld][None]

        self._ids = [id_]
        self._init_values_for_edit()
        return id_

    def _commit_write(self, follow_read=None):
        vals = self._get_values_for_write()
        if not vals:
            return True

        res = self.write(vals)
        if not res:
            return res

        for fld in self._values_to_write:
            self._columns[fld]._commit(self)

        self._init_values_for_edit()
        return res

    def commit(self):
        print('commit', self.id)
        if self.id:
            return self._commit_write()
        else:
            return self._commit_create()

    # for odoo method

    @classmethod
    def _get_domain(cls, field, context=None):
        # 仅被 get_selection 使用

        # 在多公司时, 用户可能 用 allowed_company_ids 中的一个
        # 允许 用户 在前端 自己在 allowed_company_ids 中 选择 默认的公司
        # 该选择 需要 存储在 本地 config 中

        #  全部 odoo 只有这4个 模型 在获取 fields_get时, 需要提供 globals_dict, 设置 domain
        #  其余的只是需要 company_id
        #  --- res.partner
        #  <-str---> state_id [('country_id', '=?', country_id)]

        #  --- sale.order.line
        #  <-str---> product_uom [('category_id', '=', product_uom_category_id)]

        #  --- purchase.order.line
        #  <-str---> product_uom [('category_id', '=', product_uom_category_id)]

        #  --- stock.move
        #  <-str---> product_uom [('category_id', '=', product_uom_category_id)]

        def _get_company_id():
            session_info = cls._odoo.session_info
            # company_id = session_info['company_id']
            user_companies = session_info['user_companies']
            current_company = user_companies['current_company'][0]
            # allowed_companies = user_companies['allowed_companies']
            # allowed_company_ids = [com[0] for com in allowed_companies]
            return current_company

        def _get_res_model_id():
            if cls._model_id:
                return cls._model_id

            model_id = cls._odoo.execute(
                'ir.model', 'search', [('model', '=', cls._name)])
            model_id = model_id and model_id[0]
            cls._model_id = model_id
            return model_id

        company_id = _get_company_id()
        res_model_id = _get_res_model_id()

        # print('res_model', company_id, res_model_id)

        # 已 测试完成模型: TBD, 2021-2-19
        # 1 sale.order
        # 2 sale.order.line 需要 product_uom_category_id

        globals_dict = {'company_id': company_id,
                        'res_model_id': res_model_id}

        Field = cls._columns[field]
        domain = getattr(Field, 'domain', False)

        if domain and isinstance(domain, str):
            domain = eval(domain, globals_dict, context or {})

        return domain

    @classmethod
    def get_selection(cls, field_name, context=None):
        """
        """

        fs = field_name.split('.')

        if len(fs) > 1:
            parent_field, child_field = fs
            Relation = cls.env[cls._columns[parent_field].relation]
            selection = Relation.get_selection(child_field, context=context)
            return selection
        else:
            domain = cls._get_domain(field_name, context=context)
            relation = cls._columns[field_name].relation
            context = cls._columns[field_name].context

            # print('Selection meta:', field_name, relation, domain, context)
            selection = cls.env[relation].name_search(args=domain)
            # print('Selection meta:', field_name, selection)
            return selection

    @classmethod
    def _get_field_onchange(cls, view_form_xml_id, from_record=None):
        if from_record:
            parent = from_record[0]
            field = from_record[1]

            parent_field_onchange = parent.field_onchange

            if not parent_field_onchange:
                return None

            field_onchange = dict((k.split('.')[1], v) for k, v in parent_field_onchange.items()
                                  if len(k.split('.')) == 2 and k.split('.')[0] == field.name)

            return field_onchange

        if not view_form_xml_id:
            return None

        field_onchange = cls._field_onchanges.get(view_form_xml_id)
        if field_onchange:
            return field_onchange

        if len(view_form_xml_id.split('.')) > 1:
            view = cls.env.ref(view_form_xml_id)
            view_id = view.id
        else:
            view_id = None

        args = view_id and [view_id] or []
        view_info = cls.fields_view_get(*args)
        field_onchange = cls._onchange_spec(view_info)

        cls._field_onchanges[view_form_xml_id] = field_onchange
        return field_onchange

    @classmethod
    def _onchange_spec(cls, view_info):
        """ Return the onchange spec from a view description.
        """
        result = {}

        # for traversing the XML arch and populating result
        def process(node, info, prefix):
            if node.tag == 'field':
                name = node.attrib['name']
                names = "%s.%s" % (prefix, name) if prefix else name
                if not result.get(names):
                    result[names] = node.attrib.get('on_change')
                # traverse the subviews included in relational fields
                for subinfo in info['fields'][name].get('views', {}).values():
                    process(etree.fromstring(subinfo['arch']), subinfo, names)
            else:
                for child in node:
                    process(child, info, prefix)

        process(etree.fromstring(view_info['arch']), view_info, '')
        return result

    def _onchange2(self, values, field_name, field_onchange):
        # 新增时 触发 _onchange2, 传参数 values={}, field_name=[]
        # 对于 odoo 14 直接 发请求 onchange
        # 对于 odoo 13, 调用 _default_get_onchange: 先 default_get 再 onchange

        # print('_onchange2,', self, values, field_name, field_onchange, )

        session_info = self._odoo.session_info
        # print(session_info)

        server_version_info = session_info['server_version_info']
        version = server_version_info[0]

        is_call_default = not field_name and version == 13
        # print('_onchange2', self.ids, field_name)
        # print('_onchange2, is_call_default', is_call_default)

        if is_call_default:  # 新建时 且是 odoo 13
            onchange = self._default_get_onchange(values, field_onchange)
            return onchange

        if not self.id or is_virtual_id(self.id):
            onchange = self.__class__.onchange(
                [], values, field_name, field_onchange)
            return onchange

        onchange = self.onchange(values, field_name, field_onchange)
        return onchange

    def _default_get_onchange(self, values, field_onchange):
        # 该函数 仅在 odoo 13 中 使用

        # odoo 14 中 , 新增时, 没有 default_get, 直接 onchange
        # 在 odoo 14:
        #   ids, values, field_name, field_onchange = [], {}, [], {...}
        #   so.onchange(ids, values, field_name, field_onchange)
        # 等价于 odoo 13 中的:
        #   fields = [...]
        #   values = so.default(fields)
        #   ids, values, field_name, field_onchange = [], values, fields, {...}
        #   so.onchange(ids, values, field_name, field_onchange)

        # print('_default_get_onchange', self, values)
        fields = [fld for fld in field_onchange if len(fld.split('.')) <= 1]
        # for f in fields:
        #     print(f)
        default_get = self.__class__.default_get(fields)
        # print('_default_get_onchange, defget', default_get)

        # self._odoo.print_dict(default_get)

        if not values:
            values = {}

        def _get_default(col):
            meta = self._columns[col]
            if meta.type == 'many2many':
                return [(6, False, [])]
            elif meta.type == 'one2many':
                return []
            elif meta.type in ['float', 'integer', 'monetary']:
                return 0
            elif meta.type in ['text', 'html']:
                return ''

            return False

        values_onchange = dict((col, _get_default(col))for col in fields)
        values_onchange.update(values)

        # TBD: default_get 里面 可能有 m2o o2m 需要处理
        values_onchange.update(default_get)

        if self._from_record:
            parent = self._from_record[0]
            field = self._from_record[1]

            # field.relation_field
            # print(' _default_get_onchange,parent, field.relation_field',
            #   parent, field.relation_field)
            parent_vals = parent._get_values_for_onchange(for_parent=True)
            # print(' _trigger_onchange parent_vals', parent_vals)
            # self._odoo.print_dict(
            #     parent_vals, '_default_get_onchange, parent_vals')
            values_onchange.update({
                field.relation_field: parent_vals
            })

        field_name = fields
        # print2('_default_get_onchange')
        # self._odoo.print_dict(values_onchange, '_default_get_onchange',)

        onchange = self.__class__.onchange(
            [], values_onchange, field_name, field_onchange)

        # print('xxxxxx, onchange', onchange)

        def m2o(f, v):
            return self._columns[f].type == 'many2one' and v and [v, ''] or v

        default_get2 = dict((f, m2o(f, v)) for f, v in default_get.items())

        values_ret = {}
        values_ret.update(values)
        values_ret.update(default_get2)
        values_ret.update(onchange.get('value', {}))
        onchange2 = onchange.copy()
        onchange2['value'] = values_ret
        # print(onchange2)

        return onchange2
