# -*- coding: utf-8 -*-

from odoo import tools, models, fields, api
from datetime import date, timedelta


class EquipmentHistory(models.Model):
    _name = "equipment.history"
    _description = "Equipment history"

    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment')
    effective_from = fields.Date('Effective From', required=True)
    effective_to = fields.Date('Effective To')
    current_employee = fields.Boolean('Current Employee', default=True)
    employee = fields.Many2one('hr.employee', 'Employee', required=True)
    mt_sequence_no = fields.Char("Maintenance No.")
    v9_id = fields.Integer('ID from V9')

    # ticket_no = fields.Char("Ticket No.", required=True)

    # Commented for script
    def create(self, data):
        equipment_id = data[0]['equipment_id']
        history_id = self.env['equipment.history'].search([('current_employee', '=', True),
                                                           ('equipment_id', '=', equipment_id)])
        for record in history_id:
            record.write({'effective_to': date.today() - timedelta(days=1),
                          'current_employee': False})

        return super(EquipmentHistory, self).create(data)


class ResCompany(models.Model):
    _inherit = 'res.company'

    code = fields.Char('Code')


class IrRule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def archive_rule(self):
        if self.env.ref('maintenance.equipment_rule_admin_user', raise_if_not_found=False):
            self.env.ref('maintenance.equipment_rule_admin_user').update({'active': False})
        if self.env.ref('maintenance.equipment_request_rule_admin_user', raise_if_not_found=False):
            self.env.ref('maintenance.equipment_request_rule_admin_user').update({'active': False})
        if self.env.ref('maintenance.equipment_request_rule_user', raise_if_not_found=False):
            self.env.ref('maintenance.equipment_request_rule_user').update({'active': False})
        if self.env.ref('maintenance.equipment_rule_user', raise_if_not_found=False):
            self.env.ref('maintenance.equipment_rule_user').update({'active': False})
