from odoo import tools, models, fields, api, _
from datetime import datetime, timedelta, date
import traceback
from math import ceil
import calendar
import logging
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class AttendanceMonthlySummary(models.Model):
    _name = 'attendance.monthly.summary'
    _description = 'Attendance Monthly Summary'

    def _get_time_spend(self):
        res = {}
        # for rec in self.browse(cr, uid, ids, context=context):
        # cr.execute("UPDATE public.attendance_monthly_summary SET businessdays= " + str(11)+ " WHERE id =" + str(rec.id) +";")
        return res

    # @api.model
    # def default_get(self,cr, uid, fields, EmpUniqueMonthId, context=None):
    # 	res = super(attendance_monthlySummary, self).default_get(cr, uid, fields, EmpUniqueMonthId, context=None)

    # 	dailySumm = self.pool.get('attendance.daily_summary')
    # 	dailySummSearchObj = dailySumm.search(cr, uid, [('mnthly_summ_id','=',EmpUniqueMonthId)],context=context)
    # 	if dailySummSear
    # 	chObj:
    # 		dailySummDataObj = dailySumm.browse(cr, uid, dailySummSearchObj, context=context)
    # 	dailyRecs =[]
    # 	for rec in dailySummDataObj:
    # 		line = (0, 0, {
    # 			'name':rec.name,
    # 			'file_id':rec.file_id,
    # 			'emp_id': rec.emp_id,
    # 			'date':rec.date,
    # 			'in_time':rec.in_time,
    # 			'out_time':rec.out_time,
    # 			'total_time':rec.total_time,
    # 			'total_break':rec.total_break,
    # 			'break_time':rec.break_time,
    # 			'creation_date':rec.creation_date,
    # 			'net_time':rec.net_time,
    # 			'total_break_time_decimal':rec.total_break_time_decimal,
    # 			'total_time_decimal' :rec.total_time_decimal,
    # 			'net_time_decimal':rec.net_time_decimal,
    # 			'assumed_working_time':rec.assumed_working_time,
    # 			'assumed_working_time_decimal':rec.assumed_working_time_decimal,
    # 			'mnthly_summ_id':rec.mnthly_summ_id,
    # 			'is_needs_to_be_cancel' : rec.is_needs_to_be_cancel,
    # 			'is_approved_leave' : rec.is_approved_leave,
    # 			'attendance_leave_status':rec.attendance_leave_status,
    # 		})
    # 		dailyRecs.append(line)
    # 	res.update({
    # 		'daily_summary_record':dailyRecs,
    # 	})
    # 	return res

    name = fields.Char("Name")
    employee = fields.Many2one('hr.employee', "Employee")
    daily_summary_record = fields.One2many('attendance.daily.summary', 'related_field', "Daily Records")
    month = fields.Date("Month")
    working_days = fields.Float("Working Days")
    business_days = fields.Integer("Total Days")
    lms_leave = fields.Float("Approved Leaves")
    confirm_leave = fields.Float("Unapproved Leaves")
    un_applied_leave = fields.Float("Un applied Leaves")
    total_working_hours = fields.Float("Total Working Hours")
    working_hours = fields.Float("Working Hours")
    net_working_hours = fields.Float("Net Working Hours")
    total_break_time = fields.Float("Total Break Time")
    file_id = fields.Many2one('attendance.biometric.file', 'File', readonly=True)
    assumed_working_time_decimal = fields.Float("Assumed Working Hours Decimal")

    def check_working_day(self, data_date):
        is_working = False
        date_code = 'W' + str(self.week_of_month(data_date)) + data_date.strftime("%A")[:3]
        sql = 'SELECT "' + date_code + '" FROM public.res_company where id = ' + str(self.env.user.company_id.id)
        self.cr._execute(sql)
        rows = self.cr.fetchall()
        for i in rows[0]:
            if i:
                is_working = True
        return is_working

    def week_of_month(self, data_date):

        first_day = data_date.replace(day=1)
        dom = data_date.day
        adjusted_dom = dom + first_day.weekday()
        return int(ceil(adjusted_dom / 7.0))

    def get_business_days(self, start_date, temp_emp_id):
        """ calculate business days"""
        hr_employee_obj = self.env['hr.employee'].search([('id', '=', temp_emp_id)])
        d_summary_obj = self.env['attendance.daily.summary'].search([()])
        count = 1
        data = {}
        for record in d_summary_obj:
            if datetime.strptime(record.date, '%Y-%m-%d').month == datetime.strptime(start_date,
                                                                                     '%Y-%m-%d').month and datetime.strptime(
                record.date, '%Y-%m-%d').year == datetime.strptime(start_date, '%Y-%m-%d').year:
                data[count] = record.date
                count = count + 1
        min_date = min(data.items(), key=lambda x: x[1])
        max_date = max(data.items(), key=lambda x: x[1])

        minimum_date = datetime.strptime(min_date[1], '%Y-%m-%d')
        maximum_date = datetime.strptime(max_date[1], '%Y-%m-%d')
        start_date_obj = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        month = start_date_obj.month
        year = start_date_obj.year
        start_day, num_days = calendar.monthrange(year, month)
        first_date = date(int(year), int(month), int(1))
        last_date = date(int(year), int(month), int(num_days))
        business_days = 0
        diff = last_date - first_date
        for i in range(diff.days + 1):
            data_date = first_date + timedelta(i)
            if self.check_working_day(data_date):
                business_days += 1
        total_day = business_days - 1
        new_date = None

        if hr_employee_obj.join_training_date:
            new_date = hr_employee_obj.join_training_date
        elif new_date is None and hr_employee_obj.join_date:
            new_date = hr_employee_obj.join_date

        j_date = datetime.strptime(new_date, '%Y-%m-%d')
        if new_date and j_date.month == datetime.strptime(start_date, '%Y-%m-%d').month and j_date:
            if j_date.month == datetime.strptime(start_date, '%Y-%m-%d').month:
                if j_date > minimum_date:
                    day_generator = (j_date + timedelta(x + 1) for x in range((maximum_date - j_date).days))
                    total_day = sum(1 for day in day_generator if day.weekday() < 5)

        if hr_employee_obj.leaving_date:
            l_date = datetime.strptime(hr_employee_obj.leaving_date, '%Y-%m-%d')
            if l_date.month == datetime.strptime(start_date, '%Y-%m-%d').month:
                if maximum_date > l_date:
                    day_generator = (minimum_date + timedelta(x + 1) for x in range((l_date - minimum_date).days))
                    total_day = sum(1 for day in day_generator if day.weekday() < 5) + 1
        return total_day + 1

    def create_monthly_summary(self, temp_emp_id, start_date, business_days, un_applied_leave_count,
                               un_approved_leave_count, confirm_leave_count, public_holiday_count, working_day_count,
                               net_working_hours, working_hours, total_break_time, file_id, awt_decimal):
        """ create monthly summary """

        start_date_obj = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        month = start_date_obj.month
        year = start_date_obj.year

        hr_employee_obj = self.env['hr.employee'].search([('id', '=', temp_emp_id)])
        try:
            month_date = str(date(year, month, 1))
            name = hr_employee_obj.name
            if float(working_day_count) > float(business_days - public_holiday_count):

                working_day_count = working_day_count - un_applied_leave_count - confirm_leave_count

            else:
                if float(business_days - public_holiday_count - un_applied_leave_count - confirm_leave_count) > float(
                        working_day_count) or float(
                    business_days - public_holiday_count - un_applied_leave_count - confirm_leave_count) == float(
                    working_day_count) or float(
                    business_days - public_holiday_count - un_applied_leave_count - confirm_leave_count) == float(
                    working_day_count) and (un_applied_leave_count + confirm_leave_count) == 0:
                    pass

                else:
                    working_days = float(
                        business_days - public_holiday_count - un_applied_leave_count - confirm_leave_count)

            self.create({
                'name': str(name) + " " + "on" + " " + str(month_date),
                'employee': temp_emp_id,
                'month': month_date,
                'working_days': working_day_count,
                'business_days': business_days - public_holiday_count,
                'lms_leave': confirm_leave_count,
                'confirm_leave': un_approved_leave_count,
                'un_applied_leave': un_applied_leave_count,
                'total_working_hours': (working_day_count) * 9,
                'net_working_hours': net_working_hours,
                'working_hours': working_hours,
                'total_break_time': total_break_time,
                'assumed_working_time_decimal': awt_decimal,
                'file_id': file_id,
                # 'daily_summary_record': dailySummDataObj
            })
        except Exception as e:
            _logger.info(traceback.format_exc())
            _logger.info('Something is wrong')
            _logger.info(str(e))

    def attendance_monthly_summary_scheduler(self, file_ids=None):

        daily_sum_obj = self.env['attendance.daily.summary']
        hr_employee_obj = self.env['hr.employee'].search([])
        try:
            for emp in hr_employee_obj:
                daily_sum_data_obj = daily_sum_obj.search([('status', '=', False), ('emp_id', '=', emp.id)],
                                                          order="date asc")
                start_date = ' '
                temp_emp_id = ' '
                net_working_hours = 0.0
                working_hours = 0.0
                total_break_time = 0.0
                file_id = ' '
                emp_join_date = ''
                awt_decimal = 0.0
                emp_last_date = ''
                count = 1
                working_day_count = 0
                confirm_leave_count = 0
                un_approved_leave_count = 0
                un_applied_leave_count = 0
                public_holiday_count = 0
                if daily_sum_data_obj:
                    # iterate daily summary record
                    for record in daily_sum_data_obj:
                        if start_date == ' ':
                            emp_join_date = record.emp_id.join_date
                            emp_last_date = record.emp_id.leaving_date
                            if not emp_join_date:
                                emp_join_date = record.emp_id.join_training_date
                            start_date = record.date
                            file_id = record.file_id.id
                        # check start date is not equals to blank
                        if start_date != ' ':
                            start_date_obj = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
                            end_date = record.date
                            end_date_obj = datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT)
                            start_date_month = start_date_obj.month
                            start_date_year = start_date_obj.year
                            end_date_month = end_date_obj.month
                            end_date_year = end_date_obj.year
                            # check below condition if excel sheet get more than one month employee data
                            if end_date_month > start_date_month or end_date_year > start_date_year and end_date_month < start_date_month:
                                business_days = self.get_business_days(start_date, temp_emp_id)
                                join_date = datetime.strptime(emp_join_date, DEFAULT_SERVER_DATE_FORMAT)
                                if emp_last_date:
                                    last_date = datetime.strptime(emp_last_date, DEFAULT_SERVER_DATE_FORMAT)
                                else:
                                    last_date = None
                                if start_date in emp_join_date and join_date.day > 1:
                                    self.calculate_first_time_employee_monthly_summary(temp_emp_id,
                                                                                       start_date,
                                                                                       confirm_leave_count,
                                                                                       un_applied_leave_count,
                                                                                       un_approved_leave_count,
                                                                                       business_days,
                                                                                       public_holiday_count,
                                                                                       working_day_count,
                                                                                       net_working_hours,
                                                                                       working_hours,
                                                                                       total_break_time, file_id,
                                                                                       awt_decimal)
                                elif last_date != None:
                                    self.calculate_last_time_employee_monthly_summary(temp_emp_id,
                                                                                      start_date,
                                                                                      confirm_leave_count,
                                                                                      un_applied_leave_count,
                                                                                      un_approved_leave_count,
                                                                                      business_days,
                                                                                      public_holiday_count,
                                                                                      working_day_count,
                                                                                      net_working_hours,
                                                                                      working_hours,
                                                                                      total_break_time, file_id,
                                                                                      awt_decimal)
                                else:
                                    self.create_monthly_summary(temp_emp_id, start_date, business_days,
                                                                un_applied_leave_count, un_approved_leave_count,
                                                                confirm_leave_count, public_holiday_count,
                                                                working_day_count, net_working_hours, working_hours,
                                                                total_break_time, file_id, awt_decimal)
                                temp_emp_id = record.emp_id.id
                                start_date = record.date
                                emp_join_date = record.emp_id.join_date
                                emp_last_date = record.emp_id.leaving_date
                                awt_decimal = record.assumed_working_time_decimal
                                if not emp_join_date:
                                    emp_join_date = record.emp_id.join_training_date
                                file_id = record.file_id.id
                                working_day_count = 0
                                un_applied_leave_count = 0
                                un_approved_leave_count = 0
                                confirm_leave_count = 0
                                public_holiday_count = 0
                                net_working_hours = 0.0
                                working_hours = 0.0
                                total_break_time = 0.0
                        # check last employee id is equals to current record employee id or employee id is blank
                        if temp_emp_id == record.emp_id.id or temp_emp_id == ' ':
                            file_id = record.file_id.id
                            temp_emp_id = record.emp_id.id
                            count += 1
                            working_hours += record.total_time_decimal
                            net_working_hours += record.net_time_decimal
                            total_break_time += record.total_break_time_decimal
                            awt_decimal += record.assumed_working_time_decimal
                            if record.attendance_leave_status == "Present":
                                working_day_count += 1
                            elif record.attendance_leave_status == "Public Holiday":
                                public_holiday_count += 1
                            elif (
                                    record.attendance_leave_status != "Present" and record.attendance_leave_status != "Public Holiday") and (
                                    record.is_approved_leave is True):
                                confirm_leave_count += 1
                            elif (
                                    record.attendance_leave_status != "Present" and record.attendance_leave_status != "Public Holiday" and record.attendance_leave_status != "Unapplied Leave") and (
                                    record.is_approved_leave is False):
                                un_approved_leave_count += 1
                            elif (
                                    record.attendance_leave_status != "Present" and record.attendance_leave_status != "Public Holiday") and (
                                    record.is_approved_leave is False):
                                un_applied_leave_count += 1
                        else:
                            business_days = self.get_business_days(start_date, temp_emp_id)
                            join_date = datetime.strptime(emp_join_date, DEFAULT_SERVER_DATE_FORMAT)

                            if emp_last_date:
                                last_date = datetime.strptime(emp_last_date, DEFAULT_SERVER_DATE_FORMAT)
                            else:
                                last_date = None

                            if start_date in emp_join_date and join_date.day > 1:
                                self.calculate_first_time_employee_monthly_summary(temp_emp_id, start_date,
                                                                                   confirm_leave_count,
                                                                                   un_applied_leave_count,
                                                                                   un_approved_leave_count,
                                                                                   business_days,
                                                                                   public_holiday_count,
                                                                                   working_day_count,
                                                                                   net_working_hours, working_hours,
                                                                                   total_break_time, file_id,
                                                                                   awt_decimal)
                            elif last_date is not None:
                                self.calculate_last_time_employee_monthly_summary(temp_emp_id, start_date,
                                                                                  confirm_leave_count,
                                                                                  un_applied_leave_count,
                                                                                  un_approved_leave_count,
                                                                                  business_days,
                                                                                  public_holiday_count,
                                                                                  working_day_count,
                                                                                  net_working_hours, working_hours,
                                                                                  total_break_time, file_id,
                                                                                  awt_decimal)
                            else:
                                self.create_monthly_summary(temp_emp_id, start_date, business_days,
                                                            un_applied_leave_count, un_approved_leave_count,
                                                            confirm_leave_count, public_holiday_count,
                                                            working_day_count, net_working_hours, working_hours,
                                                            total_break_time, file_id, awt_decimal)
                            temp_emp_id = record.emp_id.id
                            start_date = record.date
                            file_id = record.file_id.id
                            count = 1
                            working_hours = record.total_time_decimal
                            net_working_hours = record.net_time_decimal
                            total_break_time = record.total_break_time_decimal
                            emp_join_date = record.emp_id.join_date
                            if not emp_join_date:
                                emp_join_date = record.emp_id.join_training_date
                    business_days = self.get_business_days(start_date, temp_emp_id)
                    join_date = datetime.strptime(emp_join_date, DEFAULT_SERVER_DATE_FORMAT)
                    if emp_last_date:
                        last_date = datetime.strptime(emp_last_date, DEFAULT_SERVER_DATE_FORMAT)
                    else:
                        last_date = None
                    if start_date in emp_join_date and join_date.day > 1:
                        self.calculate_first_time_employee_monthly_summary(temp_emp_id, start_date,
                                                                           confirm_leave_count, un_applied_leave_count,
                                                                           un_approved_leave_count, business_days,
                                                                           public_holiday_count, working_day_count,
                                                                           net_working_hours, working_hours,
                                                                           total_break_time, file_id, awt_decimal)
                    elif last_date is not None:
                        self.calculate_last_time_employee_monthly_summary(temp_emp_id, start_date,
                                                                          confirm_leave_count,
                                                                          un_applied_leave_count,
                                                                          un_approved_leave_count, business_days,
                                                                          public_holiday_count, working_day_count,
                                                                          net_working_hours, working_hours,
                                                                          total_break_time, file_id, awt_decimal)
                    else:
                        self.create_monthly_summary(temp_emp_id, start_date, business_days,
                                                    un_applied_leave_count, un_approved_leave_count,
                                                    confirm_leave_count, public_holiday_count, working_day_count,
                                                    net_working_hours, working_hours, total_break_time, file_id,
                                                    awt_decimal)
                    # update daily summary record status
                    for daily_record in daily_sum_data_obj:
                        self.update_attendance_daily_summary_status()

        except Exception as e:
            _logger.info(traceback.format_exc())
            _logger.info('Something is wrong')
            _logger.info(str(e))

    def calculate_last_time_employee_monthly_summary(self, temp_emp_id, start_date, confirm_leave_count,
                                                     un_applied_leave_count, un_approved_leave_count, business_days,
                                                     public_holiday_count, working_day_count, net_working_hours,
                                                     working_hours, total_break_time, file_id, awt_decimal):
        start_date_obj = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        month = start_date_obj.month
        year = start_date_obj.year
        try:
            month_date = str(date(year, month, 1))
            hr_employee_obj = self.env['hr.employee'].search([('id', '=', temp_emp_id)])
            name = hr_employee_obj.name
            name_obj = str(name) + " " + "on" + " " + str(month_date)
            self.create({
                'name': name_obj,
                'employee': temp_emp_id,
                'month': month_date,
                'working_days': working_day_count,
                'business_days': business_days - public_holiday_count,
                'lms_leave': confirm_leave_count,
                'un_applied_leave': un_applied_leave_count,
                'total_working_hours': (working_day_count) * 9,
                'net_working_hours': net_working_hours,
                'working_hours': working_hours,
                'total_break_time': total_break_time,
                'assumed_working_time_decimal': awt_decimal,
                'file_id': file_id
            })
        except Exception as e:
            _logger.info(traceback.format_exc())
            _logger.info('Something is wrong')
            _logger.info(str(e))

    def calculate_first_time_employee_monthly_summary(self, temp_emp_id, start_date, confirm_leave_count,
                                                      un_applied_leave_count, un_approved_leave_count, businessdays,
                                                      public_holiday_count, working_day_count, net_working_hours,
                                                      working_hours, total_break_time, file_id, awt_decimal):

        start_date_obj = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        month = start_date_obj.month
        year = start_date_obj.year
        try:
            month_date = str(date(year, month, 1))
            hr_employee_obj = self.env['hr.employee'].search([('id', '=', temp_emp_id)])
            name = hr_employee_obj.name
            nameObj = str(name) + " " + "on" + " " + str(month_date)

            self.create({
                'name': nameObj,
                'employee': temp_emp_id,
                'month': month_date,
                'working_days': working_day_count,
                'business_days': businessdays - public_holiday_count,
                'lms_leave': confirm_leave_count,
                'un_applied_leave': un_applied_leave_count,
                'total_working_hours': (working_day_count) * 9,
                'net_working_hours': net_working_hours,
                'working_hours': working_hours,
                'total_break_time': total_break_time,
                'assumed_working_time_decimal': awt_decimal,
                'file_id': file_id
            })
        except Exception as e:
            _logger.info(traceback.format_exc())
            _logger.info('Something is wrong')
            _logger.info(str(e))

    def update_attendance_daily_summary_status(self):
        """ update attendance daily summary record status """
        try:
            self.write({
                'status': True})
        except Exception as e:
            _logger.info('Something is wrong')
            _logger.info(traceback.format_exc())
            _logger.info(str(e))
