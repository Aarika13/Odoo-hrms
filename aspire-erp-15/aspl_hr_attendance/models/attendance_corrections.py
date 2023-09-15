# -*- coding: utf-8 -*-

from odoo import fields, models, api, _, exceptions
from datetime import datetime, timedelta
import logging
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_TIME_FORMAT
from odoo.tools import format_datetime

_logger = logging.getLogger(__name__)


class AttendanceCorrections(models.Model):
    """Attendance corrections"""
    _name = 'attendance.corrections'
    _description = 'Attendance Correction'
    _inherit = 'mail.thread'

    def _default_employee(self):
        return self.env.user.employee_id

    @api.depends('in_time', 'out_time')
    def _compute_total_time(self):
        for wfh in self:
            if wfh.out_time and wfh.in_time:
                delta = wfh.out_time - wfh.in_time
                wfh.total_time = delta.total_seconds() / 3600.0
            else:
                wfh.total_time = False

    def _record_name(self):
        for record in self:
            name = record.employee_id.name
            in_time = record.in_time
            date = in_time.date()
            name_with_date = str(name) + " " + "corrections" + " on " + str(date)
            record.name = name_with_date

    def _get_logged_in_user(self):
        for record in self:
            if record.user_id.id == self.env.user.id:
                record.logged_in_user = True
            else:
                record.logged_in_user = False

    name = fields.Char(compute='_record_name', string='Name')
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
                                  ondelete='cascade', index=True)
    in_time = fields.Datetime("Check In", required=True)
    out_time = fields.Datetime("Check Out", required=True)
    work_state = fields.Selection(
        [('new', 'New'), ('to_submit', 'Submitted'), ('approved', 'Approved'), ('considered', 'Considered'),
         ('rejected', 'Rejected')], default='new', string='Status', readonly=True)
    user_id = fields.Many2one(related='employee_id.user_id', string='User', store=True)
    total_time = fields.Float(string='Duration', compute='_compute_total_time', store=True, readonly=True)
    logged_in_user = fields.Boolean(compute='_get_logged_in_user', readonly=True)
    note = fields.Text('Note')
    attendance_id = fields.Many2one('hr.attendance', string="Attendance")
    v9_correction_id = fields.Integer()

    @api.constrains('in_time', 'out_time')
    def _check_validity_start_date_end_date(self):
        """ verifies if out_time is earlier than in_time. """
        for wfh in self:
            if wfh.in_time and wfh.out_time:
                if wfh.out_time < wfh.in_time:
                    raise exceptions.ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))

    @api.constrains('in_time', 'out_time', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        for correction in self:
            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
            last_attendance_before_check_in = self.env['hr.attendance'].search([
                ('employee_id', '=', correction.employee_id.id),
                ('check_in', '<=', correction.in_time)
            ], order='check_in desc', limit=1)
            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > correction.in_time:
                raise exceptions.ValidationError(
                    _("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                        'empl_name': correction.employee_id.name,
                        'datetime': format_datetime(self.env, correction.in_time, dt_format=False),
                    })
            if not correction.out_time:
                # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                no_check_out_attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', correction.employee_id.id),
                    ('check_out', '=>', False)
                ], order='check_in desc', limit=1)
                if no_check_out_attendances:
                    raise exceptions.ValidationError(
                        _("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                            'empl_name': correction.employee_id.name,
                            'datetime': format_datetime(self.env, no_check_out_attendances.check_in, dt_format=False),
                        })
            else:
                # we verify that the latest attendance with check_in time before our check_out time
                # is the same as the one before our check_in time computed before, otherwise it overlaps
                last_attendance_before_check_out = self.env['hr.attendance'].search([
                    ('employee_id', '=', correction.employee_id.id),
                    ('check_in', '<', correction.out_time)
                ], order='check_in desc', limit=1)
                if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                    raise exceptions.ValidationError(
                        _("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                            'empl_name': correction.employee_id.name,
                            'datetime': format_datetime(self.env, last_attendance_before_check_out.check_in,
                                                        dt_format=False),
                        })

    def check_attendance(self):
        """ submit work from home attendance """
        yesterday = datetime.strptime(str(self.in_time), DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=1)
        yesterday_beginning = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
        yb = yesterday_beginning.strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.strptime(str(self.in_time), DEFAULT_SERVER_DATETIME_FORMAT)
        today_beginning = datetime(today.year, today.month, today.day, 0, 0, 0, 0)
        tb = today_beginning.strftime("%Y-%m-%d %H:%M:%S")
        hr_attendance_obj = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id),
                                                              ('check_in', '>=', tb),
                                                              ('check_in', '<', yb)], order="check_in asc")
        if hr_attendance_obj:
            flag = True
            in_list = []
            out_list = []
            in_count = 0
            out_count = 0
            in_list.append(datetime.strptime(str(self.in_time), DEFAULT_SERVER_DATETIME_FORMAT))
            out_list.append(datetime.strptime(str(self.out_time), DEFAULT_SERVER_DATETIME_FORMAT))
            in_list = sorted(in_list)
            out_list = sorted(out_list)
            for i in range(0, len(in_list) * 2):
                if i % 2 == 0:
                    if i == 0:
                        pass
                    else:
                        if in_list[in_count] > out_list[out_count - 1]:
                            pass
                        else:
                            flag = False
                    in_count = in_count + 1

                else:
                    if in_list[in_count - 1] < out_list[out_count]:
                        pass
                    else:
                        flag = False
                    out_count = out_count + 1
            return flag
        else:
            return False

    def submit(self):
        """ submit work from home attendance """
        if self.check_attendance():
            self.write({'work_state': 'to_submit'})
        else:
            raise exceptions.ValidationError(_('You have entered an invalid sign-in or sign-out time !'))
        return True

    def reject(self):
        """ reject Corrections attendance """
        if self.attendance_id:
            self.attendance_id.unlink()
            self.write({'work_state': 'rejected'})
            # self.update_daily_summary()
            # self.update_monthly_summary()
        else:
            raise exceptions.ValidationError(_('Related Attendance does not exists'))
        return True

    def set_to_default(self):
        self.write({'work_state': 'new'})
        return True

    # def update_monthly_summary(self):
    #     update_sql = 'UPDATE public.attendance_daily_summary SET "dailySumm_status"= False WHERE EXTRACT(MONTH FROM date)=' + str(
    #         datetime.strptime(self.in_time,
    #                           DEFAULT_SERVER_DATETIME_FORMAT).month) + ' and EXTRACT(YEAR FROM date) = ' + str(
    #         datetime.strptime(self.in_time,
    #                           DEFAULT_SERVER_DATETIME_FORMAT).year) + ' and emp_id = ' + str(
    #         self.employee_id.id) + ';'
    #     self.cr._execute(update_sql)
    #     delete_sql = 'DELETE FROM public.attendance_monthly_summary WHERE EXTRACT(MONTH FROM month) = ' + str(
    #         datetime.strptime(self.in_time,
    #                           DEFAULT_SERVER_DATETIME_FORMAT).month) + ' and EXTRACT(YEAR FROM month) = ' + str(
    #         datetime.strptime(self.in_time,
    #                           DEFAULT_SERVER_DATETIME_FORMAT).year) + ' and employee = ' + str(
    #         self.employee_id.id) + ';'
    #     self.cr._execute(delete_sql)
    #     # Need to fix
    #     # self.pool.get('attendance.monthly.summary').attendance_monthly_summary_scheduler(file_ids=None)

    # def update_daily_summary(self):
    #     yesterday = datetime.strptime(self.in_time, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=1)
    #     yesterday_beginning = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0, 0)
    #     yb = yesterday_beginning.strftime("%Y-%m-%d %H:%M:%S")
    #     today = datetime.strptime(self.in_time, DEFAULT_SERVER_DATETIME_FORMAT)
    #     today_beginning = datetime(today.year, today.month, today.day, 0, 0, 0, 0)
    #     tb = today_beginning.strftime("%Y-%m-%d %H:%M:%S")
    #
    #     hr_attendance_obj = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id),
    #                                                           ('name', '>=', tb),
    #                                                           ('name', '<', yb)], order="name asc")
    #     if hr_attendance_obj:
    #         update_sql = 'UPDATE public.hr_attendance SET atten_status = False WHERE id in' + str(
    #             hr_attendance_obj).replace("[", "(").replace("]", ")") + ';'
    #         self.cr._execute(update_sql)
    #         att_daily_summary = self.env['attendance.daily_summary'].search([('emp_id', '=', self.employee_id.id),
    #                                                                          ('date', '=', today_beginning.date())],
    #                                                                         limit=1)
    #         if att_daily_summary:
    #             att_daily_summary.unlink()
    #         Need to fix
    #         self.pool.get('attendance.daily_summary').attendance_daily_summary_scheduler(cr, uid, context=None)

    def approve(self):
        for rec in self:
            if rec.user_id.id == self.env.user.id:
                raise exceptions.ValidationError(
                    _('Can not approve own Attendance.'))
            else:
                hr_attendance_obj = self.env['hr.attendance']
                attendance_id = hr_attendance_obj.create({
                    'check_in': self.in_time,
                    'check_out': self.out_time,
                    'employee_id': self.employee_id.id,
                    'atten_status': False,
                    'comment': "corrections"
                })
                self.write({'work_state': 'considered',
                            # 'record_status': True,
                            'attendance_id': attendance_id.id})
        self.write({'work_state': 'approved'})
        return True

    def unlink(self):
        for record in self:
            if record.work_state in ['approved', 'considered']:
                raise exceptions.ValidationError(_('Approved or Considered records cannot be deleted'))
        return super(AttendanceCorrections, self).unlink()

    @api.model
    def action_attendance_corrections(self):
        for wfh in self:
            if wfh.work_state == 'to_submit':
                wfh.approve()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
