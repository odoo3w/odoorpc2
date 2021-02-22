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


"""
The `odoorpc2` module defines the :class:`ODOO` class 
inherited from `odoorpc.ODOO` .

Here's a sample session using this module same to `odoorpc`::
    >>> import odoorpc2
    >>> odoo = odoorpc2.ODOO('localhost', port=8069)  # connect to localhost, default port
    >>> odoo.login('dbname', 'admin', 'admin')

new api::
    >>> odoo.session_info

"""

__author__ = 'Master Zhang'
__email__ = 'odoowww@163.com'
__licence__ = 'LGPL v3'
__version__ = '0.7.0'

__all__ = ['ODOO', 'error']


import logging

from odoorpc2.odoo import ODOO
from odoorpc import error

logging.getLogger(__name__).addHandler(logging.NullHandler())
