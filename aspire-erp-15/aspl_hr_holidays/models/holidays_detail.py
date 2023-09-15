# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrHolidaysDetail(models.Model):
    _name = "hr.holidays.detail"
    _description = "Holidays Detail"

    holiday_status_id = fields.Many2one('hr.leave.type', string='Holiday')
    name = fields.Char(string='Holiday Type', default="Holiday Leave", readonly=True)
    leave_status = fields.Char(string='Holiday Status', default='Holiday -')
    holiday_from = fields.Date(string='From Date', required=True)
    des = fields.Char(string='Description', required=True)
    color_name = fields.Selection([('red', 'Red'),
                                   ('blue', 'Blue'),
                                   ('lightgreen', 'Light Green'),
                                   ('lightblue', 'Light Blue')],
                                  default='red',
                                  string='Color in Report')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
