from odoo import api, fields, models, tools, _


class AttendanceSummary(models.Model):
    _name = "attendance.summary"
    _description = "Attendance Summary"
    _auto = False

    employee_id = fields.Many2one('hr.employee')
    employee = fields.Char(string="Employee")
    date = fields.Date(string="Date")
    hours = fields.Float(string="Working Hours")
    leave_days = fields.Float(string="Leave Days")
    leave_hours = fields.Float(string="Leave Hours")
    working_days = fields.Float(string="Working Days")

    def init(self):
        tools.drop_view_if_exists(self._cr, 'attendance_summary')
        self._cr.execute(""" CREATE OR REPLACE VIEW attendance_summary AS (
        select
        ROW_NUMBER() OVER (ORDER BY employee_id, date) AS id, employee_id,
        employee,date,leave_days,leave_hours,hours,working_days
        from(
         
        SELECT
            
            COALESCE(atten.employee_id,leave.employee_id) employee_id,
            COALESCE(atten.name,leave.name) employee,
            COALESCE(atten.date,leave.date) date,
            hours,number_of_days leave_days,leave_hours,
            case when number_of_days > 0 and number_of_days < 1 then -0.5 else working_days end working_days
            FROM
                (SELECT
                ROW_NUMBER() OVER (ORDER BY employee_id, date) AS id,
                employee_id,
                name,
                date_trunc('day',check_in) date,
                ROUND(CAST(EXTRACT(EPOCH FROM (check_out - check_in)) / 3600 AS NUMERIC), 2) AS hours,working_days
                FROM (
                    SELECT
                    he.id employee_id,he.name,
                    DATE(log_date::timestamp) AS date,
                    MIN(CASE WHEN direction = 'in' THEN log_date::timestamp ELSE NULL END) AS check_in,
                    MAX(CASE WHEN direction = 'out' THEN log_date::timestamp ELSE NULL END) AS check_out, 1 working_days
                    FROM
                        attendance_log ab join hr_employee he on ab.employee = he.id
                        WHERE
                            direction IN ('in', 'out')
                        GROUP BY
                            he.id,
                            date
                    ) als WHERE check_in is not null and check_out is not null
                )atten 
            full join (
                SELECT 
                    he.id employee_id,he.name, date_trunc('day',date_from ) date,hl.number_of_days,hl.number_of_days*rc.hours_per_day leave_hours
                FROM 
                    hr_employee he join resource_calendar rc on he.resource_calendar_id = rc.id join hr_leave hl on hl.employee_id =he.id
                where 
                    hl.state = 'validate'
        ) leave on atten.date = leave.date and atten.employee_id = leave.employee_id) otr)""")
