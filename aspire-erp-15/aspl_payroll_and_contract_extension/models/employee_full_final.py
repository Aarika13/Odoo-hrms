from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import date


class EmployeeFullFinal(models.Model):
    _name = 'employee.full.final'
    _description = 'Employee Full Final'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee')
    separation_mode = fields.Selection(related='employee_id.separation_mode', string="Separation Mode")
    resign_date = fields.Date(related='employee_id.resignation_date', string="Resign Date")
    last_date = fields.Date(related='employee_id.tentative_leaving_date', string="Last Date")
    company_id = fields.Many2one(related='employee_id.company_id', string="Company")
    notice_period = fields.Integer(related='employee_id.resigned_notice_period', string="Notice Period")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], 'Status', readonly=True, default='draft')


    def action_done(self):
        self.state = 'done'

    def action_draft(self):
        self.state = 'draft'
