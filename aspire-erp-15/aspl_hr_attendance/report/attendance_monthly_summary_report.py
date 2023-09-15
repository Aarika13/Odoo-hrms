from odoo import api, fields, models, _


class AttendanceMonthlySummaryReport(models.Model):
    _name = 'attendance.monthly.summary.report'
    _description = "Attendance Monthly Summary Report"

    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)

    def print_report(self):
        pass

    # N2F
    # def print_report(self, cr, uid, ids, context=None):
    #     data = self.read(cr, uid, ids, context=context)[0]
    #     datas = {
    #         'ids': [],
    #         'model': 'attendance.monthly.summary.report',
    #         'form': data
    #     }
    #     return self.pool['report'].get_action(cr, uid, [], 'hr_attendance_aspire.attendance_summary_report',
    #                                           data=datas, context=context)
