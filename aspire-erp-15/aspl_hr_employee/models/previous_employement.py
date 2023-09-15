import logging

from odoo import models, fields, api, _
from dateutil import parser
from datetime import datetime
from odoo.exceptions import UserError, ValidationError, Warning

_logger = logging.getLogger(__name__)


# Previous employment detail
class PreviousEmployment(models.Model):
    _name = "previous.employment"
    _description = "Previous Employment"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    start = fields.Date('From Date', required=True)
    end = fields.Date('To Date', required=True)
    company_name = fields.Char('Company Name', required=True)
    designation = fields.Char('Designation', required=True)
    company_add = fields.Char('Company Address')
    relevant = fields.Boolean('Relevant')
    leaving_reason = fields.Char('Reason For Leaving')
    ref_name = fields.Char('Reference Name')
    ref_contact_no = fields.Char('Reference Mobile No')

    @api.onchange('start')
    def on_change_start(self):
        for record in self:
            if record.start:
                if parser.parse(record.start).date() > datetime.now().date():
                    raise ValidationError('Please Enter correct "Start Date"')

    @api.onchange('end')
    def on_change_end(self):
        for record in self:
            if record.end and record.start:
                if parser.parse(record.start).date() > parser.parse(record.end).date():
                    raise ValidationError('Please Enter correct "End Date"')

    @api.constrains('start')
    def constrains_start(self):
        for record in self:
            if record.start:
                if parser.parse(record.start).date() > datetime.now().date():
                    raise ValidationError('Please Enter correct "Start Date" in previous employment')
        return True

    @api.constrains('end')
    def constrains_end(self):
        for record in self:
            if record.end and record.start:
                if parser.parse(record.start).date() > parser.parse(record.end).date():
                    raise ValidationError('Please Enter correct "To Date" in previous employment"')
        return True
