from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    track_detailed_attendance = fields.Boolean("Track Detailed Attendance")
    biometric_no = fields.Char("Biometric Code", size=10)
    permanent_work_from_home = fields.Boolean("Permanent Work From Home")
    att_history = fields.One2many('attendance.history', 'employee_id', 'Attendance History')
