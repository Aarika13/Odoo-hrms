from odoo import api, fields, models, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import json
import logging
import traceback
import requests
_logger = logging.getLogger(__name__)

class AccountAnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = 'account.analytic.line'

    billable = fields.Boolean('Billable', default=True)
    invoiced = fields.Boolean('Invoiced')
    approved = fields.Boolean('Approved')
    invoice_id = fields.Many2one('account.invoice')
    product_type = fields.Many2one("product.product", "Product")
    user_id = fields.Many2one('res.users', string='User')
    display_name = fields.Many2one('res.users', 'Display Name' , default=lambda self: self.env.user)
    name = fields.Text('Description')   # , required=True

    # defaults = {
    #
    # 	'billable': True,
    # 	'invoiced': False,
    # 	'approved': False,
    # }
    @api.model
    def create(self,vals):
        result = super(AccountAnalyticLine,self).create(vals)
        if 'employee_id' in vals and 'name' in vals and not 'Time Off' in vals['name']:
            sheet_id = self.env["hr_timesheet.sheet"].search([
                ("date_end", ">=", vals['date']),
                ("date_start", "<=", vals['date']),
                ("employee_id", "=", vals['employee_id'])])
            timesheet_sheet_update = "UPDATE public.account_analytic_line SET sheet_id = '" + str(sheet_id.id) + "' where id = '"+ str(result.id)+"';"
            self.env.cr.execute(timesheet_sheet_update)
        return result
    

    @api.onchange('unit_amount')
    def _onchange_unit_amount(self):
        if self.account_id and self.user_id:
            self.product_uom_id = self.env['uom.uom'].search([('name', '=', 'Hour(s)')])

    @api.onchange('account_id', 'user_id')
    def _onchange_account_id(self):
        if self.account_id and self.user_id:
            project_obj = self.env['project.project'].search([('analytic_account_id', '=', self.account_id.id)])

            for record in project_obj.member_id:
                if record.name.id == self.user_id.id:
                    self.display_name = record.display_name.id
                    self.product_type = record.product_type.id

    def _check(self, cr, uid, ids):
        for att in self.browse(cr, uid, ids):
            if att.sheet_id and att.sheet_id.state not in ('draft', 'new', 'confirm', 'done'):
                raise UserError(_('You cannot modify an entry in a confirmed timesheet.'))
        return True


    def get_odoo_task_status(self, status_name):
        status_ = None
        status_obj = self.env['project.task.type']
        status_search_id = status_obj.search([('name', '=', status_name)])
        if status_search_id:
            status_data = status_obj.browse(status_search_id)
            status_name = status_data.id
        return status_name


    def action_approve_activity(self):
        data_obj = self.env['ir.model.data']
        if self._context.get('active_ids'):
            selected_records = self.search([('id', 'in', self._context.get('active_ids'))])
            activity_obj = self.env['account.analytic.line']
            for activity in selected_records:
                activity_obj.write(activity.id, {'approved': True})

    def action_billable_activity(self):
        data_obj = self.env['ir.model.data']
        if self._context.get('active_ids'):
            selected_records = self.search([('id', 'in', self._context.get('active_ids'))])
            activity_obj = self.env['account.analytic.line']
            for activity in selected_records:
                activity_obj.write(activity.id, {'billable': True})

    def action_invoiced_activity(self):
        data_obj = self.env['ir.model.data']
        if self._context.get('active_ids'):
            selected_records = self.search([('id', 'in', self._context.get('active_ids'))])
            activity_obj = self.env['account.analytic.line']
            for activity in selected_records:
                activity_obj.write(activity.id, {'invoiced': True})

# class account_analytic_account(osv.osv):
#     _name = 'account.analytic.account'
#     _inherit = ['account.analytic.account']
#
#
class timesheetEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, vals):
        employee = super(timesheetEmployee, self).create(vals)
        hr_timesheet_sheet_object = self.env['hr_timesheet.sheet']
        hr_timesheet_sheet_object.add_next_month_my_timesheet()
        return employee

    def write(self,vals):
        flag = 1 if 'user_id' in vals else 0   
        employee = super(timesheetEmployee, self).write(vals)

        _logger.info("Employeedata  =================================== %s",flag)
        if flag == 1:
            hr_timesheet_sheet_object = self.env['hr_timesheet.sheet']
            hr_timesheet_sheet_object.add_next_month_my_timesheet()
        return employee

