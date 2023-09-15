from odoo import api, fields, models, _
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class AttendanceHistory(models.Model):
    _name = "attendance.history"
    _description = "Monthly attendance"

    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    total_hours = fields.Char(string="Total Hours (Excluding Breaks)")
    total_hours_all = fields.Char(string="Total Hours (Including Breaks)")
    employee_id = fields.Many2one('hr.employee', string="Employee")

    def generate_attendance_history(self):
        date_start = date.today() - relativedelta(months=3, day=1)
        date_end = date.today() - relativedelta(months=3, day=31)

        for emp in self.env['hr.employee'].search([]):

            monthly_attendance = self.env['hr.attendance'].search([('employee_id', '=', emp.id), ('check_in', '>=', date_start), ('check_out', '<=', date_end)])
            total_hours = sum(monthly_attendance.mapped('worked_hours'))

            monthly_attendance_all = self.env['attendance.report.daywise'].search([
                ('employee', '=', emp.name),
                ('check_in', '>=', datetime.strptime(date_start.strftime("%Y-%m-%d 00:00:00"), "%Y-%m-%d %H:%M:%S")),
                ('check_out', '<=', datetime.strptime(date_end.strftime("%Y-%m-%d 23:59:59"), "%Y-%m-%d %H:%M:%S")),
            ])
            total_hours_all = sum(monthly_attendance_all.mapped('difference_hours'))

            data = {
                'start_date': date_start,
                'end_date': date_end,
                'total_hours': round(total_hours, 2),
                'total_hours_all': round(total_hours_all, 2),
                'employee_id': emp.id
            }
            if self.env['attendance.history'].search([('employee_id', '=', emp.id), ('start_date', '=', date_start), ('end_date', '=', date_end)]):
                continue
            else:
                self.env['attendance.history'].create(data)
            monthly_attendance.with_context(allow_modify_confirmed_sheet=True).unlink()
