import logging
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


# Employee family information
class EmployeeDocument(models.Model):
    _name = "employee.appraisal"
    _description = "Employee Appraisal"
    _order = "create_date desc"

    # If needed we will make appraisal date as join_date by default
    # def _default_appraisal_date(self):
    #     previous_dates = [i.appraisal_date for i in self.employee_id.appraisal_ids]
    #     if previous_dates:
    #         return previous_dates[0]
    #     else:
    #         return self.employee_id.join_date

    appraisal_date = fields.Date('Appraisal Date', default=datetime.today().date()) # default=_default_appraisal_dat
    employee_id = fields.Many2one('hr.employee', string="Employee")
    months = fields.Integer()
    document = fields.Binary()
    document_name = fields.Char('Attachment Name')
    new_ctc = fields.Integer("New CTC")
    old_ctc = fields.Integer("Old CTC")
    percentage_hike = fields.Integer("Hike %", compute="_compute_hike")
    appraisal_note = fields.Text('Appraisal Note')

    @api.onchange('appraisal_date')
    def on_change_appraisal_date(self):
        previous_dates = [i.appraisal_date for i in self.employee_id.appraisal_ids]
        old_ctc_list = [i.new_ctc for i in self.employee_id.appraisal_ids]
        for record in self:
            len_app = len(record.employee_id.appraisal_ids)
            emp_id = str(record.employee_id.id).split('_')
            emp_obj = self.env['hr.employee'].search([('id', '=', emp_id[-1])])
            new_date = record.appraisal_date + relativedelta(months=12)

            appraisal_date_day = int(new_date.strftime("%d"))
            
            if appraisal_date_day > 1 and appraisal_date_day > 15:
                date = new_date - relativedelta(days = appraisal_date_day) + relativedelta(days=1) + relativedelta(months=1)    
            elif appraisal_date_day > 1 and appraisal_date_day < 15:
                date = new_date - relativedelta(days = appraisal_date_day) + relativedelta(days=1)
            else:
                date = new_date

            if len_app > 1:
                num_months = (record.appraisal_date.year - previous_dates[0].year) * 12 + (
                        record.appraisal_date.month - previous_dates[0].month)
                record.months = num_months
                emp_obj.write({'appraisal_date': date})
                record.old_ctc = old_ctc_list[0]
            else:
                num_months = (record.appraisal_date.year - record.employee_id.join_date.year) * 12 + (
                        record.appraisal_date.month - record.employee_id.join_date.month)
                record.months = num_months
                record.old_ctc = old_ctc_list[0]
                emp_obj.write({'appraisal_date': date})

    @api.depends('new_ctc', 'old_ctc')
    def _compute_hike(self):
        for record in self:
            if record.old_ctc and record.new_ctc:
                record.percentage_hike = (record.new_ctc - record.old_ctc) / (record.old_ctc / 100)
            else:
                record.percentage_hike = 0

    # def save_appraisal(self):
    #     vals = {
    #         'appraisal_date': self.appraisal_date,
    #         'months': self.months,
    #         'document': self.document,
    #         'new_ctc': self.new_ctc,
    #         'old_ctc': self.old_ctc
    #     }
    #     self.create(vals)
    #     # emp_id = str(record.employee_id.id).split('_')
    #     # emp_obj = self.env['hr.employee'].search([('id', '=', emp_id[-1])])
    #     # date = record.appraisal_date + relativedelta(months=12)
    #     # emp_obj.write({'appraisal_due_date': date})

