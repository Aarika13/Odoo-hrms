# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,osv
from odoo import api, _
from odoo.exceptions import UserError
import re

class invoice_date_format(models.Model):
    _name = "invoice.date.format"

    name = fields.Char('Date Format')

    _sql_constraints = [
        ('name', 'unique(name)', ' This Date Format is already exist. Please enter unique Date Format.')
    ]

    @api.model
    def create(self,vals):
        record = super(invoice_date_format, self).create(vals)
        date_list=['m','mm','mmm','mmmm','yyyy','d','dd']
        if vals['name']:
            separator = re.split(r"[\w']+", vals['name'])
            if not separator:
                raise UserError(_('Please enter valid date format.'))

            date = re.findall(r"[\w']+", vals['name'])
            print("date == ",date)

            if len(date) == 1 or len(date) == 2:
                raise UserError(_('Please enter valid date format.'))

            if date[0] not in date_list or date[1] not in date_list or date[2] not in date_list:
                raise UserError(_('Please enter valid date format.'))

        print("Vals == ",vals)
        return record

    def write(self, vals):
        record = super(invoice_date_format, self).write(vals)
        date_list = ['m', 'mm','mmmm','mmm', 'yyyy', 'd', 'dd']

        if self.name:
            separator = re.split(r"[\w']+", self.name)
            if not separator:
                raise UserError(_('Please enter valid date format.'))

            date = re.findall(r"[\w']+", self.name)
            print("date == ",date)

            if len(date) == 1 or len(date) == 2:
                raise UserError(_('Please enter valid date format.'))

            if date[0] not in date_list or date[1] not in date_list or date[2] not in date_list:
                raise UserError(_('Please enter valid date format.'))

        print("Vals == ",vals)
        return record

# class res_partner(models.Model):
#     _inherit = "res.partner"

#     date_format = fields.Many2one('invoice.date.format',string='Date Format')
