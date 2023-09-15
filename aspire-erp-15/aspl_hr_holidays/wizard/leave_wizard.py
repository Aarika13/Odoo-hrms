# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError, Warning


class LeaveWizard(models.TransientModel):
    """docstring for last_month_leave_wizard"""
    _name = 'leave.wizard'
    _description = " Leave Wizard"

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    report_type = fields.Selection([
        ('approved', 'Approved'),
        ('toapprove', 'To Approve'),
        ('unapplied', 'Un Applied'),
        ('needtoreject', 'Need To Reject '),
    ], 'Report Type')

    def create_report(self, cr, uid, ids, context=None):

        data = self.read(cr, uid, ids, context=context)[0]

        datas = {
            'ids': [],
            'model': 'leave.wizard',
            'form': data
        }
        return self.env['report'].get_action(cr, uid, [],
                                              'hr_holidays_aspire.last_month_leave_summary_report_view',
                                              data=datas, context=context)

    @api.constrains('endDate')
    def _check_something(self):
        for record in self:
            if record.start_date > record.end_date:
                raise ValidationError("Enter correct end_date: %s" % record.end_date)
