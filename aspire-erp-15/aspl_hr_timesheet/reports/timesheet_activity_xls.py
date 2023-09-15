from odoo import api, fields, models, _


class TimesheetActivity(models.TransientModel):
    _name = 'timesheet.activity.xls'
    _description = "Timesheet Activity XLS"

    file = fields.Binary("File")
    file_name = fields.Char("File Name")
