from odoo import fields, api, models, _
import traceback
from datetime import datetime, timedelta, date
import logging
from math import ceil
from dateutil.rrule import rrule, DAILY
import pytz
from odoo import SUPERUSER_ID
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_TIME_FORMAT

_logger = logging.getLogger(__name__)


class AttendanceDailySummary(models.Model):
    _name = 'attendance.daily.summary'
    _description = 'Attendance Daily Summary'

    name = fields.Char("Name")
    file_id = fields.Many2one('attendance.biometric.file', 'File', readonly=True)
    emp_id = fields.Many2one('hr.employee', "Employee")
    date = fields.Date("Date")
    in_time = fields.Char("In-Time")
    out_time = fields.Char("Out-Time")
    total_time = fields.Char("Total Time")
    total_break = fields.Integer("Total Break")
    break_time = fields.Char("Break Time")
    net_time = fields.Char("Net Time")
    creation_date = fields.Date("Create Date")
    total_break_time_decimal = fields.Float("Break Time Decimal")
    total_time_decimal = fields.Float("Total Time Decimal")
    net_time_decimal = fields.Float("Net Time Decimal")
    status = fields.Boolean("Status")
    assumed_working_time_decimal = fields.Float("Assumed Working Hours Decimal")
    assumed_working_time = fields.Char("Assumed Working Hours")
    monthly_sum_id = fields.Char("Monthly Id")
    attendance_leave_status = fields.Char("Attendance Status")
    is_approved_leave = fields.Boolean("Is Approved")
    is_needs_to_be_cancel = fields.Boolean("Needs to be cancel")
    related_field = fields.Many2one('attendance.monthly.summary', "REF", default=0)

    def create_reference_number_for_monthly_summary(self, single_date, emp_num):
        sd_month = single_date.month
        sd_year = single_date.year
        unique_ref_num = emp_num + str(sd_year) + str(sd_month)
        return unique_ref_num

    def utc_to_local(self, dateTime):
        """ convert utc to local timezone """
        try:
            tz = pytz.timezone(self.env.user.partner_id.tz)
            local_dt = dateTime.replace(tzinfo=pytz.utc).astimezone(tz)
            return tz.normalize(local_dt)
        except Exception as e:
            hr_employee_obj = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            if hr_employee_obj:
                if hr_employee_obj.work_email:

                    message = (
                            "Hi " + hr_employee_obj.name +
                            ", \n\n There was an issue while procesSign attendance records."
                            " Below is the detail in brief:\n\n Timezone is not set. Make sure "
                            + hr_employee_obj.name + " has timezone assigned.")
                    vals = {
                        'subject': 'Issue in Attendance Record',
                        'body_html': '<pre>%s</pre>' % message,
                        'email_to': hr_employee_obj.work_email,
                        'email_from': 'pgandhi@aspiresoftware.in ',
                    }
                    email_ids = self.env['mail.mail'].create(vals)
                    if email_ids:
                        email_ids.send()
            _logger.error(traceback.format_exc())
            _logger.error(str(e))

    def attendance_daily_summary_scheduler(self, emp_id=None, start_date=None, file_id=None):
        """ attendance daily summary scheduler """

        hr_emp_obj = self.env['hr.employee'].search([])
        hr_attendance = self.env['hr.attendance']
        biometric_obj = self.pool.get('attendance.biometric.file')
        if start_date:
            end_date = start_date
            start_date_obj = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
            end_date_obj = datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT)

        else:
            bio_file_id = biometric_obj.browse(file_id)
            file_start_date = bio_file_id.start_date
            file_end_date = bio_file_id.end_date
            start_date_obj = datetime.strptime(file_start_date, DEFAULT_SERVER_DATE_FORMAT)
            end_date_obj = datetime.strptime(file_end_date, DEFAULT_SERVER_DATE_FORMAT)

        file_id = None
        try:

            #  Loops Over each date in range from start to end date
            for single_date in rrule(DAILY, dtstart=start_date_obj, until=end_date_obj):

                sd = datetime.strftime(single_date, DEFAULT_SERVER_DATETIME_FORMAT)
                tomorrow = single_date + timedelta(days=1)
                tomorrow_beginning = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0, 0)
                tmb = tomorrow_beginning.strftime("%Y-%m-%d %H:%M:%S")
                today = single_date
                today_beginning = datetime(today.year, today.month, today.day, 0, 0, 0, 0)
                tb = today_beginning.strftime("%Y-%m-%d %H:%M:%S")

                if emp_id:
                    hr_emp_obj = self.env['hr.employee'].search([('id', '=', emp_id)])

                #  Loops over all employees
                for emp in hr_emp_obj:

                    daily_attend_summary_obj = self.search([('emp_id', '=', emp.id), ('date', '=', single_date)])
                    if daily_attend_summary_obj:
                        daily_attend_summary_obj.unlink()

                    hr_attend_search_correction_date_obj = hr_attendance.search([('file_id', '=', None),
                                                                                 ('employee_id', '=', emp.id),
                                                                                 ('name', '>=', tb),
                                                                                 ('name', '<', tmb)],
                                                                                order="name asc")
                    hr_attend_search_date_obj = hr_attendance.search([('employee_id', '=', emp.id), ('name', '>=', tb),
                                                                      ('name', '<', tmb)], order="name asc")

                    if hr_attend_search_correction_date_obj and hr_attend_search_date_obj:
                        attend_search = list(set(hr_attend_search_date_obj) | set(hr_attend_search_correction_date_obj))
                        hr_attend_search_date_obj = hr_attendance.search([('id', 'in', attend_search)],
                                                                         order="name asc")

                    temp_emp_id = emp.id
                    on_date = single_date
                    validated_leave = self.check_employee_validate_leave(on_date, temp_emp_id)
                    confirmed_leave = self.check_employee_confirm_leave(on_date, temp_emp_id)

                    #  when data is not available
                    if not hr_attend_search_date_obj:

                        #  Check if the day is working day
                        is_working_day = self.check_working_day(on_date)

                        if not is_working_day:
                            pass

                        elif is_working_day:
                            public_holiday = self.check_public_holidays(on_date)

                            #  Check if it is Public Holiday
                            if public_holiday:
                                name_obj = str(emp.name) + " " + "on" + " " + str(
                                    datetime.strptime(sd, DEFAULT_SERVER_DATETIME_FORMAT).date())

                                emp_num = emp.employee_no
                                result = self.create_reference_number_for_monthly_summary(single_date, emp_num)
                                self.create({
                                    'name': name_obj,
                                    'file_id': file_id,
                                    'emp_id': emp.id,
                                    'date': single_date,
                                    'in_time': timedelta(0, 0, 0),
                                    'out_time': timedelta(0, 0, 0),
                                    'total_time': timedelta(0, 0, 0),
                                    'total_break': 0,
                                    'break_time': timedelta(0, 0, 0),
                                    'creation_date': 0,
                                    'net_time': timedelta(0, 0, 0),
                                    'total_break_time_decimal': 0,
                                    'total_time_decimal': 0,
                                    'net_time_decimal': 0,
                                    'assumed_working_time': timedelta(0, 0, 0),
                                    'assumed_working_time_decimal': 0,
                                    'monthly_sum_id': result,
                                    'attendance_leave_status': 'Public Holiday',
                                })

                            #  Employee on confirmed Leave
                            elif confirmed_leave:
                                approved_leave = True
                                confirm_leave_type = confirmed_leave[1]
                                name_obj = str(emp.name) + " " + "on" + " " + str(
                                    datetime.strptime(sd, DEFAULT_SERVER_DATETIME_FORMAT).date())

                                emp_num = emp.employee_no
                                result = self.create_reference_number_for_monthly_summary(single_date, emp_num)
                                self.create({
                                    'name': name_obj,
                                    'file_id': file_id,
                                    'emp_id': emp.id,
                                    'date': single_date,
                                    'in_time': timedelta(0, 0, 0),
                                    'out_time': timedelta(0, 0, 0),
                                    'total_time': timedelta(0, 0, 0),
                                    'total_break': 0,
                                    'break_time': timedelta(0, 0, 0),
                                    'creation_date': 0,
                                    'net_time': timedelta(0, 0, 0),
                                    'total_break_time_decimal': 0,
                                    'total_time_decimal': 0,
                                    'net_time_decimal': 0,
                                    'assumed_working_time': timedelta(0, 0, 0),
                                    'assumed_working_time_decimal': 0,
                                    'monthly_sum_id': result,
                                    'attendance_leave_status': confirm_leave_type,
                                    'is_approved_leave': approved_leave,
                                })

                            #  Employee on Applied Leave but not on Confirmed Leave
                            elif validated_leave:
                                validated_leave_type = validated_leave[1]
                                name_obj = str(emp.name) + " " + "on" + " " + str(
                                    datetime.strptime(sd, DEFAULT_SERVER_DATETIME_FORMAT).date())

                                emp_num = emp.employee_no
                                result = self.create_reference_number_for_monthly_summary(single_date, emp_num)
                                self.create({
                                    'name': name_obj,
                                    'file_id': file_id,
                                    'emp_id': emp.id,
                                    'date': single_date,
                                    'in_time': timedelta(0, 0, 0),
                                    'out_time': timedelta(0, 0, 0),
                                    'total_time': timedelta(0, 0, 0),
                                    'total_break': 0,
                                    'break_time': timedelta(0, 0, 0),
                                    'creation_date': 0,
                                    'net_time': timedelta(0, 0, 0),
                                    'total_break_time_decimal': 0,
                                    'total_time_decimal': 0,
                                    'net_time_decimal': 0,
                                    'assumed_working_time': timedelta(0, 0, 0),
                                    'assumed_working_time_decimal': 0,
                                    'monthly_sum_id': result,
                                    'attendance_leave_status': validated_leave_type,
                                })

                            #  Un applied Leave
                            else:
                                name_obj = str(emp.name) + " " + "on" + " " + str(
                                    datetime.strptime(sd, DEFAULT_SERVER_DATETIME_FORMAT).date())

                                emp_num = emp.employee_no
                                result = self.create_reference_number_for_monthly_summary(single_date, emp_num)
                                self.create({
                                    'name': name_obj,
                                    'file_id': file_id,
                                    'emp_id': emp.id,
                                    'date': single_date,
                                    'in_time': timedelta(0, 0, 0),
                                    'out_time': timedelta(0, 0, 0),
                                    'total_time': timedelta(0, 0, 0),
                                    'total_break': 0,
                                    'break_time': timedelta(0, 0, 0),
                                    'creation_date': 0,
                                    'net_time': timedelta(0, 0, 0),
                                    'total_break_time_decimal': 0,
                                    'total_time_decimal': 0,
                                    'net_time_decimal': 0,
                                    'assumed_working_time': timedelta(0, 0, 0),
                                    'assumed_working_time_decimal': 0,
                                    'monthly_sum_id': result,
                                    'attendance_leave_status': 'Unapplied Leave',
                                })

                    # when data is available
                    else:
                        if confirmed_leave or validated_leave:
                            needs_to_be_cancel = True
                            if hr_attend_search_date_obj and (len(hr_attend_search_date_obj) % 2 == 0):

                                name_obj = str(emp.name) + " " + "on" + " " + str(
                                    datetime.strptime(sd, DEFAULT_SERVER_DATETIME_FORMAT).date())
                                count = 0
                                file_id = None
                                out_time = None
                                date_time_obj = datetime.today()
                                date_obj = date_time_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)
                                total_break_time = timedelta(0, 0, 0)
                                in_time = timedelta(0, 0, 0)
                                assumed_working_time_decimal = 0
                                temp_date = str(datetime.strptime(sd, DEFAULT_SERVER_DATETIME_FORMAT).date())

                                for hr_attend in hr_attend_search_date_obj:
                                    count = count + 1
                                    emp_num = hr_attend.employee_id.employee_no

                                    if file_id is None:
                                        file_id = hr_attend.file_id.id

                                    if count == 1 and str(hr_attend.action) in 'sign_in':
                                        in_time = datetime.strptime(hr_attend.name, DEFAULT_SERVER_DATETIME_FORMAT)
                                    elif count == len(hr_attend_search_date_obj) and str(
                                            hr_attend.action) in 'sign_out' and type(in_time) is not timedelta:
                                        out_time = datetime.strptime(hr_attend.name, DEFAULT_SERVER_DATETIME_FORMAT)
                                        total_time = out_time - in_time
                                        net_time = total_time - total_break_time
                                        total_break = (len(hr_attend_search_date_obj) / 2) - 1
                                        total_time_decimal = self.convert_time_to_decimal(total_break_time, total_time,
                                                                                          net_time)

                                        if assumed_working_time_decimal > 1:
                                            assumed_working_time = total_time - timedelta(hours=1)
                                            assumed_working_time_decimal = total_time_decimal['totTimeDecimal'] - 1
                                        else:
                                            assumed_working_time = total_time
                                            assumed_working_time_decimal = total_time_decimal['totTimeDecimal']
                                        result = self.create_reference_number_for_monthly_summary(single_date,
                                                                                                  emp_num)

                                        self.create({
                                            'name': name_obj,
                                            'file_id': file_id,
                                            'emp_id': emp.id,
                                            'date': temp_date,
                                            'in_time': self.utc_to_local(in_time).time(),
                                            'out_time': self.utc_to_local(out_time).time(),
                                            'total_time': total_time,
                                            'total_break': int(total_break),
                                            'break_time': total_break_time,
                                            'creation_date': date_obj,
                                            'net_time': net_time,
                                            'total_break_time_decimal': total_time_decimal['totBrTimeDecimal'],
                                            'total_time_decimal': total_time_decimal['totTimeDecimal'],
                                            'net_time_decimal': total_time_decimal['netTimeDecimal'],
                                            'assumed_working_time': assumed_working_time,
                                            'assumed_working_time_decimal': assumed_working_time_decimal,
                                            'monthly_sum_id': result,
                                            'attendance_leave_status': 'Present',
                                            'is_needs_to_be_cancel': needs_to_be_cancel,
                                        })
                                    else:
                                        if str(hr_attend.action) in 'sign_out' and count > 1:
                                            out_time = datetime.strptime(hr_attend.name, DEFAULT_SERVER_DATETIME_FORMAT)
                                        elif str(hr_attend.action) in 'sign_in' and count > 1:
                                            if out_time is not None:
                                                in_time = datetime.strptime(hr_attend.name,
                                                                            DEFAULT_SERVER_DATETIME_FORMAT)
                                                break_time = in_time - out_time
                                                total_break_time = total_break_time + break_time
                                    att_id = hr_attend.id
                                    self.update_attendance_record_status(att_id)

                        else:
                            if hr_attend_search_date_obj and (len(hr_attend_search_date_obj) % 2 == 0):

                                name_obj = str(emp.name) + " " + "on" + " " + str(
                                    datetime.strptime(sd, DEFAULT_SERVER_DATETIME_FORMAT).date())

                                count = 0
                                file_id = None
                                out_time = None
                                date_time_obj = datetime.today()
                                date_obj = date_time_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)
                                total_break_time = timedelta(0, 0, 0)
                                in_time = timedelta(0, 0, 0)
                                assumed_working_time_decimal = 0
                                temp_date = str(datetime.strptime(sd, DEFAULT_SERVER_DATETIME_FORMAT).date())

                                for i in hr_attend_search_date_obj:
                                    count = count + 1
                                    emp_num = i.employee_id.employee_no

                                    if file_id is None:
                                        file_id = i.file_id.id

                                    if count == 1 and str(i.action) in 'sign_in':
                                        in_time = datetime.strptime(i.name, DEFAULT_SERVER_DATETIME_FORMAT)
                                    elif count == len(hr_attend_search_date_obj) and str(
                                            i.action) in 'sign_out' and type(
                                        in_time) is not timedelta:
                                        out_time = datetime.strptime(i.name, DEFAULT_SERVER_DATETIME_FORMAT)
                                        total_time = out_time - in_time
                                        net_time = total_time - total_break_time
                                        total_break = (len(hr_attend_search_date_obj) / 2) - 1
                                        total_time_decimal = self.convert_time_to_decimal(total_break_time, total_time,
                                                                                          net_time)

                                        if assumed_working_time_decimal > 1:
                                            assumed_working_time = total_time - timedelta(hours=1)
                                            assumed_working_time_decimal = total_time_decimal['totTimeDecimal'] - 1
                                        else:
                                            assumed_working_time = total_time
                                            assumed_working_time_decimal = total_time_decimal['totTimeDecimal']
                                        result = self.create_reference_number_for_monthly_summary(single_date,
                                                                                                  emp_num)

                                        self.create({
                                            'name': name_obj,
                                            'file_id': file_id,
                                            'emp_id': emp.id,
                                            'date': temp_date,
                                            'in_time': self.utc_to_local(in_time).time(),
                                            'out_time': self.utc_to_local(out_time).time(),
                                            'total_time': total_time,
                                            'total_break': int(total_break),
                                            'break_time': total_break_time,
                                            'creation_date': date_obj,
                                            'net_time': net_time,
                                            'total_break_time_decimal': total_time_decimal['totBrTimeDecimal'],
                                            'total_time_decimal': total_time_decimal['totTimeDecimal'],
                                            'net_time_decimal': total_time_decimal['netTimeDecimal'],
                                            'assumed_working_time': assumed_working_time,
                                            'assumed_working_time_decimal': assumed_working_time_decimal,
                                            'monthly_sum_id': result,
                                            'attendance_leave_status': 'Present',
                                        })
                                    else:
                                        if str(i.action) in 'sign_out' and count > 1:
                                            out_time = datetime.strptime(i.name, DEFAULT_SERVER_DATETIME_FORMAT)
                                        elif str(i.action) in 'sign_in' and count > 1:
                                            if out_time is not None:
                                                in_time = datetime.strptime(i.name, DEFAULT_SERVER_DATETIME_FORMAT)
                                                break_time = in_time - out_time
                                                total_break_time = total_break_time + break_time
                                    att_id = i.id
                                    self.update_attendance_record_status(att_id)

        except Exception as e:
            _logger.error(traceback.format_exc())
            _logger.error(str(e))

    def convert_time_to_decimal(self, total_break_time, total_time, net_time):
        """ convert attendance daily summary time into decimal format """
        vals = {}
        try:
            tbr_time = str(total_break_time).split(':')
            tot_time = str(total_time).split(':')
            net_time = str(net_time).split(':')

            if int(tbr_time[1]) != 0:
                vals['totBrTimeDecimal'] = round((int(tbr_time[0]) + int(tbr_time[1]) / 60.0), 2)
            else:
                vals['totBrTimeDecimal'] = int(tbr_time[0])

            if int(tot_time[1]) != 0:
                vals['totTimeDecimal'] = round((int(tot_time[0]) + int(tot_time[1]) / 60.0), 2)
            else:
                vals['totTimeDecimal'] = int(tot_time[0])

            if int(net_time[1]) != 0:
                vals['netTimeDecimal'] = round((int(net_time[0]) + int(net_time[1]) / 60.0), 2)
            else:

                vals['netTimeDecimal'] = int(net_time[0])
            return vals

        except Exception as e:
            _logger.error(traceback.format_exc())
            _logger.error(str(e))
            return False

    def update_attendance_record_status(self, att_id):
        """ update attendance record status """
        sql = 'UPDATE public.hr_attendance SET atten_status= True WHERE id  =' + str(att_id) + ';'
        try:
            self.cr._execute(sql)
        except Exception as e:
            _logger.error(traceback.format_exc())
            _logger.error(str(e))

    # -------------------------- LEAVES SECTION  ---------------------

    def check_employee_validate_leave(self, on_date, temp_emp_id):
        """ calculate total employee leaves """
        try:
            is_validated = False
            on_date = datetime.strftime(on_date, DEFAULT_SERVER_DATETIME_FORMAT)
            holidays_obj = self.env['hr.leave'].search([
                ('date_from', '=', on_date),
                ('date_to', '=', on_date),
                ('state', 'in', ['validate1', 'confirm']),
                ('employee_id', '=', temp_emp_id)])
            if holidays_obj:
                is_validated = True
                leave_type_validate = holidays_obj.holiday_status_id.name
                return is_validated, leave_type_validate
            else:
                return is_validated

        except Exception as e:
            _logger.info(traceback.format_exc())
            _logger.info('Something is wrong')
            _logger.info(str(e))
            return 0

    def check_employee_confirm_leave(self, on_date, temp_emp_id):
        """ calculate total employee leaves """
        try:
            is_confirm = False
            on_date = datetime.strftime(on_date, DEFAULT_SERVER_DATETIME_FORMAT)
            holidays_obj = self.env['hr.leave'].search([
                ('date_from', '=', on_date),
                ('date_to', '=', on_date),
                ('state', 'in', ['validate']),
                ('employee_id', '=', temp_emp_id)])

            if holidays_obj:
                is_confirm = True
                confirm_leave_type = holidays_obj.holiday_status_id.name
                return is_confirm, confirm_leave_type
            else:
                return is_confirm

        except Exception as e:
            _logger.info(traceback.format_exc())
            _logger.info('Something is wrong')
            _logger.info(str(e))
            return 0

    def check_working_day(self, on_date):
        is_working = False
        date_code = 'W' + str(self.week_of_month(on_date)) + on_date.strftime("%A")[:3]
        sql = 'SELECT "' + date_code + '" FROM public.res_company where id = ' + str(self.env.user.company_id.id)
        self.cr._execute(sql)
        rows = self.cr.fetchall()
        for i in rows[0]:
            if i:
                is_working = True

        return is_working

    def week_of_month(self, on_date):

        first_day = on_date.replace(day=1)
        dom = on_date.day
        adjusted_dom = dom + first_day.weekday()
        return int(ceil(adjusted_dom / 7.0))

    def check_public_holidays(self, on_date):
        """ calculate public holidays """

        try:
            is_public_holiday = False
            on_date = datetime.strftime(on_date, DEFAULT_SERVER_DATE_FORMAT)
            hr_holidays_detail = self.env['hr.holidays.detail'].search([
                ('holiday_from', '<=', on_date),
                ('holiday_from', '>=', on_date)])
            if hr_holidays_detail:
                is_public_holiday = True
                return is_public_holiday

            else:
                return is_public_holiday

        except Exception as e:
            _logger.info(traceback.format_exc())
            _logger.info('Something is wrong')
            _logger.info(str(e))
            return 0
