from odoo import api, fields, models, tools, _


class AttendanceReportDaywise(models.Model):
    _name = "attendance.report.daywise"
    _description = "Day wise Attendance Report"
    _auto = False

    employee = fields.Char(string='Employee Name')
    check_in = fields.Datetime("Check in")
    check_out = fields.Datetime("Check out")
    difference_hours = fields.Float('Total Time')

    def init(self):
        tools.drop_view_if_exists(self._cr, 'attendance_report_daywise')
        self._cr.execute(""" CREATE OR REPLACE VIEW attendance_report_daywise AS (SELECT
            ROW_NUMBER() OVER (ORDER BY employee, date) AS id,
            employee,
            check_in,
            check_out,
            ROUND(CAST(EXTRACT(EPOCH FROM (check_out - check_in)) / 3600 AS NUMERIC), 2) AS difference_hours
        FROM (
            SELECT
                he.name employee,
                DATE(log_date::timestamp) AS date,
                MIN(CASE WHEN direction = 'in' THEN log_date::timestamp ELSE NULL END) AS check_in,
                MAX(CASE WHEN direction = 'out' THEN log_date::timestamp ELSE NULL END) AS check_out
            FROM
                attendance_log ab join hr_employee he on ab.employee = he.id
                WHERE
                direction IN ('in', 'out')
            GROUP BY
                he.name,
                date
            union
            select he.name,
                DATE(start_date::timestamp) AS date,
                MIN(start_date)  AS check_in,
                MAX(end_date) AS check_out
            from attendance_work_from_home wfh join hr_employee he on wfh.employee_id = he.id
            where wfh.work_state in ('approved','considered')
			GROUP BY
                he.name,date
        ) als where check_in is not null and check_out is not null)""")
