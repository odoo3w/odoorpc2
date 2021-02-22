config = {}

config['sale.order'] = {
    'field_onchange_ref': 'sale.view_order_form',
}

config['sale.order.line'] = {
    'field_onchange_ref': 'sale.view_order_form',
    'field_onchange_model': 'sale.order',
    'field_onchange_field': 'order_line',
}


class Many2many(odoorpc_Many2many, BaseField):
    """Represent the OpenObject 'fields.many2many'"""

    def __get__(self, instance, owner):
        """Return a recordset."""

        print('Many2many get:', self, instance, owner)

        if not instance.field_onchange:
            return super().__get__(instance, owner)

        return self._get_for_edit(instance, owner)

    def _get_for_edit(self, instance, owner):
        """Return a recordset."""

        # TBD

        return super().__get__(instance, owner)


class Many2one(odoorpc_Many2one, BaseField):
    """Represent the OpenObject 'fields.many2one'"""

    def __get__(self, instance, owner):
        # print('Many2one get:', self, instance, owner)
        return super().__get__(instance, owner)

        # if not instance.field_onchange:
        #     return super().__get__(instance, owner)

        # # TBD 新增 和 编辑 读取 方式不一样.
        # # return self._get_for_new(instance, owner)

        # return self._get_for_edit(instance, owner)

    def _get_for_edit222(self, instance, owner):
        pass

        # print('Many2one _get_for_edit', self,
        #       self.name, instance, instance.id, owner)

        # id_ = instance._values[self.name].get(instance.id)
        # if instance.id in instance._values_to_write[self.name]:
        #     id_ = instance._values_to_write[self.name][instance.id]
        # # None value => get the value on the fly
        # if id_ is None:
        #     if instance.id:
        #         # TBD not str virtual
        #         args = [[instance.id], [self.name]]
        #         kwargs = {'context': self.context, 'load': '_classic_write'}
        #         id_ = instance._odoo.execute_kw(
        #             instance._name, 'read', args, kwargs)[0][self.name]
        #         instance._values[self.name][instance.id] = id_

        # print('Many2one _get_for_edit', id_)

        # Relation = instance.env[self.relation]
        # if id_:
        #     env = instance.env
        #     if self.context:
        #         context = instance.env.context.copy()
        #         context.update(self.context)
        #         env = instance.env(context=context)
        #     return Relation._browse(
        #         env, id_, from_record=(instance, self))
        # return Relation.browse(False)


class One2many(odoorpc_One2many, BaseField):
    """Represent the OpenObject 'fields.one2many'"""

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
        # return self._get_for_edit(instance, owner)

    def _get_for_edit22(self, instance, owner):
        pass
        """Return a recordset."""
        # # print('_get_for_edit get:', self, self.name, instance, owner)
        # ids = None
        # if instance._values[self.name].get(instance.id):
        #     ids = instance._values[self.name][instance.id][:]
        # # None value => get the value on the fly
        # if ids is None:
        #     if instance.id:
        #         # TBD not str virtual

        #         args = [[instance.id], [self.name]]
        #         kwargs = {'context': self.context, 'load': '_classic_write'}
        #         orig_ids = instance._odoo.execute_kw(
        #             instance._name, 'read', args, kwargs)[0][self.name]
        #         instance._values[self.name][instance.id] = orig_ids
        #         ids = orig_ids and orig_ids[:] or []

        # # # Take updated values into account
        # if instance.id in instance._values_to_write[self.name]:
        #     values = instance._values_to_write[self.name][instance.id]
        #     # Handle ODOO tuples to update 'ids'
        #     ids = tuples2ids(values, ids or [])

        # # print(' _get_for_edit ids ', ids)
        # # ids 包含  新增的虚拟id

        # Relation = instance.env[self.relation]
        # env = instance.env
        # if self.context:
        #     context = instance.env.context.copy()
        #     context.update(self.context)
        #     env = instance.env(context=context)

        # relation = Relation._browse(
        #     env, ids, from_record=(instance, self))
        # self._data[instance.id] = relation
        # return relation

    def __set__(self, instance, value):
        print('One2many set:', self, instance, value)

        self._old__set__(instance, value)

    def _old__set__(self, instance, value):
        #
        print('o2m set,', self, instance, value)
        # value = self.check_value(value)
        # if isinstance(value, IncrementalRecords):
        #     value = value.tuples
        # else:
        #     if value and not odoo_tuple_in(value):
        #         value = [(6, 0, records2ids(value))]
        #     elif not value:
        #         value = [(5, )]
        # instance._values_to_write[self.name][instance.id] = value
        super(One2many, self).__set__(instance, value)
