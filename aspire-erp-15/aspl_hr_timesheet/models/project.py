from datetime import date
import logging

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class Project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    description = fields.Html("Description")
    start_date = fields.Date("Planned Start Date")
    end_date = fields.Date("Planned End Date")
    estimated_time = fields.Float("Estimated time")
    amount = fields.Float("Amount")
    sales_person = fields.Many2one("res.users", "Sales Person")
    project_tag = fields.Char("Tag")
    attach_timesheet_to_invoice = fields.Boolean("Attach Timesheet To Invoice")
    per_resource = fields.Boolean("Per Resource")
    consolidate = fields.Boolean("Consolidate")
    show_un_billed_hours = fields.Boolean("Show Un-billed Hours")
    actual_start_date = fields.Date("Actual Start Date", default=date.today())
    actual_end_date = fields.Date("Actual End Date")
    partner_id = fields.Many2one('res.partner', 'Customer')     # domain=[('customer', '=', True)]

    # _defaults = {
    #     'actual_start_date': date.today(),
    # }


#
# class hr_timesheet_sheet_sheet_account(osv.osv):
#     _name = "hr_timesheet_sheet.sheet.account"
#     _inherit = "hr_timesheet_sheet.sheet.account"
