# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from pytz import utc
from odoo import models, fields, api, _
from odoo.http import request
from odoo.tools import float_utils

ROUNDING_FACTOR = 16


class HrLeave(models.Model):
    _inherit = 'hr.leave'
    duration_display = fields.Char('Requested (Days/Hours)', compute='_compute_duration_display', store=True,
                                   help="Field allowing to see the leave request duration"
                                        " in days or hours depending on the leave_type_request_unit")

class Employee(models.Model):
    _inherit = 'hr.employee'

    birthday = fields.Date('Date of Birth', groups="base.group_user", help="Birthday")

    @api.model
    def check_user_group(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)


        # ======================================================== Adding Manual ======================================================== #

        if user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            return "main_hr"
        elif user.has_group('hr_recruitment.group_hr_recruitment_user'):
            return "jr_hr"
        else:
            return False
        
        # ================================================================================================================================ #
        

    @api.model
    def get_user_employee_details(self):
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        leaves_to_approve = self.env['hr.leave'].sudo().search_count([('state', 'in', ['confirm', 'validate1'])])
        today = datetime.strftime(datetime.today(), '%Y-%m-%d')
        query = """
        select count(id)
        from hr_leave
        WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) OVERLAPS ('%s', '%s') and
        state='validate'""" % (today, today)
        cr = self._cr
        cr.execute(query)
        leaves_today = cr.fetchall()   
        # timesheets_today = cr.fetchall() ###
        first_day = datetime.today().replace(day=1)
        last_day = (datetime.today() + relativedelta(months=1, day=1)) - timedelta(1)
        query = """
                select count(id)
                from hr_leave
                WHERE (hr_leave.date_from::DATE,hr_leave.date_to::DATE) OVERLAPS ('%s', '%s')
                and  state='validate'""" % (first_day, last_day)
        cr = self._cr
        cr.execute(query)
        timesh_mon_cou = 0
        leaves_this_month = cr.fetchall()
        leaves_alloc_req = self.env['hr.leave.allocation'].sudo().search_count(
            [('state', 'in', ['confirm', 'validate1'])])
        
        timesheet_count = self.env['account.analytic.line'].sudo().search_count(
            [('project_id', '!=', False) , ('user_id', '=', uid)])
        
        timesheet_today_count = self.env['account.analytic.line'].sudo().search_count(
            [('project_id', '!=', False) , ('date' , '=' , datetime.today()) ,('user_id', '=', uid)])
        
        # ********************************************************** ADD MANUAL ***************************************************************

        # ********************* TABLE ********************* #
        loop = []
        stages = []
        dict = {}

        if ( Employee.check_user_group(self) == "main_hr" ):
            for i in self.env['job.opening'].sudo().search([]):
                loop.append(i.name)
            
        elif ( Employee.check_user_group(self) == "jr_hr" ):
            for i in self.env['job.opening'].sudo().search(
                [('user_id', '=', uid),('active','=',True)]):
                loop.append(i.name)
            
        for i in self.env['hr.recruitment.stage'].sudo().search([]):
            stages.append(i.name)

        if ( Employee.check_user_group(self) == "main_hr" ):
            for i in range(len(loop)):
                dict.update({i:{0:loop[i]}})
                for j in stages:
                    first = self.env['hr.applicant'].sudo().search_count(
                    [('active','=',True),('job_opening_id', '=', loop[i]),('stage_id','=', j)])
                    dict[i][j] = first

        elif ( Employee.check_user_group(self) == "jr_hr" ):
            for i in range(len(loop)):
                dict.update({i:{0:loop[i]}})
                for j in stages:
                    first = self.env['hr.applicant'].sudo().search_count(
                    [('user_id', '=', uid),('active','=',True),('job_opening_id', '=', loop[i]),('stage_id','=', j)])
                    dict[i][j] = first

        # print("*************STAGES**************",stages)
        # print("*************DICT**************",dict)
        
        # ********************* TABLE OF ACTIVITY ********************* #
        #         # ************ OLD CODE ************ #
        # # emp_name_temp = []
        # users = []
        # activity_types = []
        # dict_of_activity = {}

        # # for i in self.env['mail.activity'].sudo().search([
        # #     ('res_model', '=', 'hr.applicant'),
        # #     ('user_id','=',self.env.context['uid']),
        # #     ('date_deadline','>=',datetime.now()),
        # #     ]):
        # #     emp_name_temp.append(i.res_name)
        # # emp_name = list(set(emp_name_temp))

        # for i in self.env['res.users'].sudo().search([]):
        #     users.append(i.name)

        # for i in self.env['mail.activity.type'].sudo().search(['|', ('res_model', '=', False), ('res_model', '=', 'hr.applicant')]):
        #     activity_types.append([i.id,i.name])

        # # for i in range(len(emp_name)):
        # #     dict_of_activity.update({i:{0:emp_name[i]}})
        # #     # print("*************dict_of_activity**************",dict_of_activity)
        # #     for j in activity_types:
        # #         temp_dict = self.env['mail.activity'].sudo().search_count(
        # #         [('res_model', '=', 'hr.applicant'),('user_id','=',self.env.context['uid']),('date_deadline','>=',datetime.now()),('res_name', '=', emp_name[i]),('activity_type_id','=', j[1])])
        # #         dict_of_activity[i][j[1]] = temp_dict

        # for i in range(len(users)):
        #     dict_of_activity.update({i:{0:users[i]}})
        #     for j in activity_types:
        #         temp_dict = self.env['mail.activity'].sudo().search_count(
        #         [('res_model', '=', 'hr.applicant'),('user_id','=',users[i]),('date_deadline','>=',datetime.now()),('activity_type_id','=', j[1])])
        #         dict_of_activity[i][j[1]] = temp_dict

                      # ************ NEW CODE ************ #
        if ( Employee.check_user_group(self) == "main_hr" ):
            users_temp = []
            activity_types_temp = []
            activity_types = []
            dict_of_activity = {}

            for i in self.env['hr.applicant'].sudo().search([]):
                users_temp.append(i.user_id.name)
            users = list(set(users_temp))

            for i in self.env['mail.activity'].sudo().search([
                ('res_model', '=', 'hr.applicant'),
                ('date_deadline','>=',datetime.now())
            ]):
                activity_types_temp.append(i.activity_type_id.name)
            for i in activity_types_temp: 
                if i not in activity_types: 
                    activity_types.append(i) 

            for i in range(len(users)):
                dict_of_activity.update({i:{0:users[i]}})
                for j in activity_types:
                    temp_dict = self.env['mail.activity'].sudo().search_count(
                    [('res_model', '=', 'hr.applicant'),('user_id','=',users[i]),('date_deadline','>=',datetime.now()),('activity_type_id','=', j)])
                    dict_of_activity[i][j] = temp_dict
            # print("*************dict_of_activity**************",dict_of_activity)

        # ********************* SAPRATE ACTIVITY TABLE ********************* #
        saprate_activity_type_temp = []
        saprate_activity_type_temp_2 = []
        saprate_activity = []

        for i in self.env['mail.activity'].sudo().search([
            ('res_model', '=', 'hr.applicant'),
            ('user_id','=',self.env.context['uid']),
            ('date_deadline','>=',datetime.now())
        ]):
            saprate_activity_type_temp.append(i.activity_type_id.name)
            for i in saprate_activity_type_temp: 
                if i not in saprate_activity_type_temp_2: 
                    saprate_activity_type_temp_2.append(i)

        for i in saprate_activity_type_temp_2:
            temp_numeric = self.env['mail.activity'].sudo().search_count([
                ('res_model', '=', 'hr.applicant'),
                ('user_id','=',self.env.context['uid']),
                ('date_deadline','>=',datetime.now()),
                ('activity_type_id','=',i)
            ])
            saprate_activity.append([i,temp_numeric])
        # print("*************** saprate_activity ***************",saprate_activity)

        # ********************* TODAY TIME OFF TABLE ********************* #
        today_time_off_emp = []

        for i in self.env['hr.leave'].sudo().search([
            ('date_from'[:10],'<=',datetime.now().strftime("%Y-%m-%d")),
            ('date_to'[:10],'>=',datetime.now().strftime("%Y-%m-%d"))
        ]):
            # print("=========date_from================",i.date_from)
            if (i.request_unit_half == False):
                today_time_off_emp.append([i.employee_id.name,i.holiday_status_id.display_name,"Full Day"])
            else :
                if (i.request_date_from_period == "am"):
                    today_time_off_emp.append([i.employee_id.name,i.holiday_status_id.display_name,"Morning"])
                else :
                    today_time_off_emp.append([i.employee_id.name,i.holiday_status_id.display_name,"Afternoon"])
        # print("***************today_time_off_emp*********************",today_time_off_emp)

        # ********************* UPCOMING EVENTS ********************* #
        upcoming_events = []

        for i in self.env['calendar.event'].sudo().search([
            '|','|',
            ('name','ilike', 'Birthday'),
            ('name','ilike', 'Marriage'),
            ('name','ilike', 'Joining'),
            ('start'[:10],'=',datetime.now().strftime("%Y-%m-%d")),
            # ('start','like',datetime.strftime(datetime.today(), '%Y-%m')),
            ]):
                event_holder_name = i.name.split(' - ')
                upcoming_events.append([event_holder_name[0],event_holder_name[1]])
        upcoming_events.sort()
        # print("***************upcoming_events*********************",upcoming_events)

        # ********************************************************************************************************************************* #

        months_count = self.env['account.analytic.line'].sudo().search(
            [('project_id', '!=', False), 
             ('date' , 'like' , datetime.strftime(datetime.today(), '%Y-%m')) , 
             ('user_id', '=', uid)])
        for i in months_count:
            a = i.unit_amount
            timesh_mon_cou = a + timesh_mon_cou
            # print("***************total*****************",a)
        timesheet_month_count = timesh_mon_cou
        timesh_mon_cou = 0

        # timesheet_month_count = self.env['account.analytic.line'].sudo().search_count(
        #     [('project_id', '!=', False), 
        #      ('date' , 'like' , datetime.strftime(datetime.today(), '%Y-%m')) , 
        #      ('user_id', '=', uid)])
        
        # date = self.env['account.analytic.line'].search([])
        # for date in date:
        #     print("date  ============ ",date.date)
        # print("timesheet_month_count == ",timesheet_month_count,datetime.strftime(datetime.today(), '%m-%d'))
        
        timesheet_view_id = self.env.ref('hr_timesheet.hr_timesheet_line_search')
        job_applications = self.env['hr.applicant'].sudo().search_count([])
        if employee:
            sql = """select broad_factor from hr_employee_broad_factor where id =%s"""
            self.env.cr.execute(sql, (employee[0]['id'],))
            result = self.env.cr.dictfetchall()
            broad_factor = result[0]['broad_factor']
            if employee[0]['birthday']:
                diff = relativedelta(datetime.today(), employee[0]['birthday'])
                age = diff.years
            else:
                age = False
            if employee[0]['joining_date']:
                diff = relativedelta(datetime.today(), employee[0]['joining_date'])
                years = diff.years
                months = diff.months
                days = diff.days
                experience = '{} years {} months {} days'.format(years, months, days)
            else:
                experience = False
            if employee:
                if ( Employee.check_user_group(self) == "main_hr" ):
                    data = {
                        'broad_factor': broad_factor if broad_factor else 0,
                        'leaves_to_approve': leaves_to_approve,
                        'leaves_today': leaves_today,
                        # 'timesheets_today': timesheets_today,   #####
                        'leaves_this_month': leaves_this_month,
                        'leaves_alloc_req': leaves_alloc_req,
                        'emp_all_timesheets': timesheet_count,
                        'emp_today_timesheets': timesheet_today_count,
                        'emp_month_timesheets': timesheet_month_count,
                        'job_applications': job_applications,
                        'timesheet_view_id': timesheet_view_id,
                        'experience': experience,
                        'age': age,
                        ######## ADD MANUALLY ######## 
                        'saprate_activity':saprate_activity,
                        'loop':dict,
                        'stages':stages,
                        'activity_types':activity_types,
                        'dict_of_activity':dict_of_activity,
                        'today_time_off_emp':today_time_off_emp,
                        'upcoming_events':upcoming_events,
                        ##############################
                    }
                elif ( Employee.check_user_group(self) == "jr_hr" ):
                    data = {
                        'broad_factor': broad_factor if broad_factor else 0,
                        'leaves_to_approve': leaves_to_approve,
                        'leaves_today': leaves_today,
                        # 'timesheets_today': timesheets_today,   #####
                        'leaves_this_month': leaves_this_month,
                        'leaves_alloc_req': leaves_alloc_req,
                        'emp_all_timesheets': timesheet_count,
                        'emp_today_timesheets': timesheet_today_count,
                        'emp_month_timesheets': timesheet_month_count,
                        'job_applications': job_applications,
                        'timesheet_view_id': timesheet_view_id,
                        'experience': experience,
                        'age': age,
                        ######## ADD MANUALLY ######## 
                        'saprate_activity':saprate_activity,
                        'loop':dict,
                        'stages':stages,
                        'today_time_off_emp':today_time_off_emp,
                        'upcoming_events':upcoming_events,
                        ##############################
                    }
                employee[0].update(data)
            return employee
        else:
            return False

    @api.model
    def get_upcoming(self):
        cr = self._cr
        uid = request.session.uid
        employee = self.env['hr.employee'].search([('user_id', '=', uid)], limit=1)

        cr.execute("""select *,
        (to_char(dob,'ddd')::int-to_char(now(),'ddd')::int+total_days)%total_days as dif
        from (select he.id, he.name, to_char(he.birthday, 'Month dd') as birthday,
        hj.name as job_id , he.birthday as dob,
        (to_char((to_char(now(),'yyyy')||'-12-31')::date,'ddd')::int) as total_days
        FROM hr_employee he
        join hr_job hj
        on hj.id = he.job_id
        ) birth
        where (to_char(dob,'ddd')::int-to_char(now(),'DDD')::int+total_days)%total_days between 0 and 15
        order by dif;""")
        birthday = cr.fetchall()
        # e.is_online # was there below
        #        where e.state ='confirm' on line 118/9 #change
        cr.execute("""select e.name, e.date_begin, e.date_end, rc.name as location
        from event_event e
        left join res_partner rp
        on e.address_id = rp.id
        left join res_country rc
        on rc.id = rp.country_id
        and (e.date_begin >= now()
        and e.date_begin <= now() + interval '15 day')
        or (e.date_end >= now()
        and e.date_end <= now() + interval '15 day')
        order by e.date_begin """)
        event = cr.fetchall()
        announcement = []
        if employee:
            department = employee.department_id
            job_id = employee.job_id
            sql = """select ha.name, ha.announcement_reason
            from hr_announcement ha
            left join hr_employee_announcements hea
            on hea.announcement = ha.id
            left join hr_department_announcements hda
            on hda.announcement = ha.id
            left join hr_job_position_announcements hpa
            on hpa.announcement = ha.id
            where ha.state = 'approved' and
            ha.date_start <= now()::date and
            ha.date_end >= now()::date and
            (ha.is_announcement = True or
            (ha.is_announcement = False
            and ha.announcement_type = 'employee'
            and hea.employee = %s)""" % employee.id
            if department:
                sql += """ or
                (ha.is_announcement = False and
                ha.announcement_type = 'department'
                and hda.department = %s)""" % department.id
            if job_id:
                sql += """ or
                (ha.is_announcement = False and
                ha.announcement_type = 'job_position'
                and hpa.job_position = %s)""" % job_id.id
            sql += ')'
            cr.execute(sql)
            announcement = cr.fetchall()
        return {
            'birthday': birthday,
            'event': event,
            'announcement': announcement
        }

    @api.model
    def get_dept_employee(self):
        cr = self._cr
        cr.execute("""select department_id, hr_department.name,count(*)
from hr_employee join hr_department on hr_department.id=hr_employee.department_id
group by hr_employee.department_id,hr_department.name""")
        dat = cr.fetchall()
        data = []
        for i in range(0, len(dat)):
            data.append({'label': dat[i][1], 'value': dat[i][2]})
        return data

    @api.model
    def get_department_leave(self):
        month_list = []
        graph_result = []
        for i in range(5, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        self.env.cr.execute("""select id, name from hr_department where active=True """)
        departments = self.env.cr.dictfetchall()
        department_list = [x['name'] for x in departments]
        for month in month_list:
            leave = {}
            for dept in departments:
                leave[dept['name']] = 0
            vals = {
                'l_month': month,
                'leave': leave
            }
            graph_result.append(vals)
        sql = """
        SELECT h.id, h.employee_id,h.department_id
             , extract('month' FROM y)::int AS leave_month
             , to_char(y, 'Month YYYY') as month_year
             , GREATEST(y                    , h.date_from) AS date_from
             , LEAST   (y + interval '1 month', h.date_to)   AS date_to
        FROM  (select * from hr_leave where state = 'validate') h
             , generate_series(date_trunc('month', date_from::timestamp)
                             , date_trunc('month', date_to::timestamp)
                             , interval '1 month') y
        where date_trunc('month', GREATEST(y , h.date_from)) >= date_trunc('month', now()) - interval '6 month' and
        date_trunc('month', GREATEST(y , h.date_from)) <= date_trunc('month', now())
        and h.department_id is not null
        """
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()
        leave_lines = []
        for line in results:
            employee = self.browse(line['employee_id'])
            from_dt = fields.Datetime.from_string(line['date_from'])
            to_dt = fields.Datetime.from_string(line['date_to'])
            days = employee.get_work_days_dashboard(from_dt, to_dt)
            line['days'] = days
            vals = {
                'department': line['department_id'],
                'l_month': line['month_year'],
                'days': days
            }
            leave_lines.append(vals)
        if leave_lines:
            df = pd.DataFrame(leave_lines)
            rf = df.groupby(['l_month', 'department']).sum()
            result_lines = rf.to_dict('index')
            for month in month_list:
                for line in result_lines:
                    if month.replace(' ', '') == line[0].replace(' ', ''):
                        match = list(filter(lambda d: d['l_month'] in [month], graph_result))[0]['leave']
                        dept_name = self.env['hr.department'].browse(line[1]).name
                        if match:
                            match[dept_name] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[:3] + " " + \
                                result['l_month'].split(' ')[1:2][0]

        return graph_result, department_list

    def get_work_days_dashboard(self, from_datetime, to_datetime, compute_leaves=False, calendar=None, domain=None):
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = calendar._attendance_intervals_batch(from_full, to_full, resource)
        day_total = defaultdict(float)
        for start, stop, meta in intervals[resource.id]:
            day_total[start.date()] += (stop - start).total_seconds() / 3600
        if compute_leaves:
            intervals = calendar._work_intervals_batch(from_datetime, to_datetime, resource, domain)
        else:
            intervals = calendar._attendance_intervals_batch(from_datetime, to_datetime, resource)
        day_hours = defaultdict(float)
        for start, stop, meta in intervals[resource.id]:
            day_hours[start.date()] += (stop - start).total_seconds() / 3600
        days = sum(
            float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day]) / ROUNDING_FACTOR
            for day in day_hours
        )
        return days

    @api.model
    def employee_leave_trend(self):
        leave_lines = []
        month_list = []
        graph_result = []
        for i in range(5, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        uid = request.session.uid
        employee = self.env['hr.employee'].sudo().search_read([('user_id', '=', uid)], limit=1)
        for month in month_list:
            vals = {
                'l_month': month,
                'leave': 0
            }
            graph_result.append(vals)
        sql = """
                SELECT h.id, h.employee_id
                     , extract('month' FROM y)::int AS leave_month
                     , to_char(y, 'Month YYYY') as month_year
                     , GREATEST(y                    , h.date_from) AS date_from
                     , LEAST   (y + interval '1 month', h.date_to)   AS date_to
                FROM  (select * from hr_leave where state = 'validate') h
                     , generate_series(date_trunc('month', date_from::timestamp)
                                     , date_trunc('month', date_to::timestamp)
                                     , interval '1 month') y
                where date_trunc('month', GREATEST(y , h.date_from)) >= date_trunc('month', now()) - interval '6 month' and
                date_trunc('month', GREATEST(y , h.date_from)) <= date_trunc('month', now())
                and h.employee_id = %s
                """
        self.env.cr.execute(sql, (employee[0]['id'],))
        results = self.env.cr.dictfetchall()
        for line in results:
            employee = self.browse(line['employee_id'])
            from_dt = fields.Datetime.from_string(line['date_from'])
            to_dt = fields.Datetime.from_string(line['date_to'])
            days = employee.get_work_days_dashboard(from_dt, to_dt)
            line['days'] = days
            vals = {
                'l_month': line['month_year'],
                'days': days
            }
            leave_lines.append(vals)
        if leave_lines:
            df = pd.DataFrame(leave_lines)
            rf = df.groupby(['l_month']).sum()
            result_lines = rf.to_dict('index')
            for line in result_lines:
                match = list(filter(lambda d: d['l_month'].replace(' ', '') == line.replace(' ', ''), graph_result))
                if match:
                    match[0]['leave'] = result_lines[line]['days']
        for result in graph_result:
            result['l_month'] = result['l_month'].split(' ')[:1][0].strip()[:3] + " " + \
                                result['l_month'].split(' ')[1:2][0]
        return graph_result

    @api.model
    def join_resign_trends(self):
        cr = self._cr
        month_list = []
        join_trend = []
        resign_trend = []
        for i in range(11, -1, -1):
            last_month = datetime.now() - relativedelta(months=i)
            text = format(last_month, '%B %Y')
            month_list.append(text)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            join_trend.append(vals)
        for month in month_list:
            vals = {
                'l_month': month,
                'count': 0
            }
            resign_trend.append(vals)
        cr.execute('''select to_char(joining_date, 'Month YYYY') as l_month, count(id) from hr_employee
        WHERE joining_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
        AND CURRENT_DATE + interval '1 month - 1 day'
        group by l_month''')
        join_data = cr.fetchall()
        cr.execute('''select to_char(resign_date, 'Month YYYY') as l_month, count(id) from hr_employee
        WHERE resign_date BETWEEN CURRENT_DATE - INTERVAL '12 months'
        AND CURRENT_DATE + interval '1 month - 1 day'
        group by l_month;''')
        resign_data = cr.fetchall()

        for line in join_data:
            match = list(filter(lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ', ''), join_trend))
            if match:
                match[0]['count'] = line[1]
        for line in resign_data:
            match = list(filter(lambda d: d['l_month'].replace(' ', '') == line[0].replace(' ', ''), resign_trend))
            if match:
                match[0]['count'] = line[1]
        for join in join_trend:
            join['l_month'] = join['l_month'].split(' ')[:1][0].strip()[:3]
        for resign in resign_trend:
            resign['l_month'] = resign['l_month'].split(' ')[:1][0].strip()[:3]
        graph_result = [{
            'name': 'Join',
            'values': join_trend
        }, {
            'name': 'Resign',
            'values': resign_trend
        }]

        return graph_result

    @api.model
    def get_attrition_rate(self):

        month_attrition = []
        monthly_join_resign = self.join_resign_trends()
        month_join = monthly_join_resign[0]['values']
        month_resign = monthly_join_resign[1]['values']
        sql = """
        SELECT (date_trunc('month', CURRENT_DATE))::date - interval '1' month * s.a AS month_start
        FROM generate_series(0,11,1) AS s(a);"""
        self._cr.execute(sql)
        month_start_list = self._cr.fetchall()
        for month_date in month_start_list:
            self._cr.execute("""select count(id), to_char(date '%s', 'Month YYYY') as l_month from hr_employee
            where resign_date> date '%s' or resign_date is null and joining_date < date '%s'
            """ % (month_date[0], month_date[0], month_date[0],))
            month_emp = self._cr.fetchone()
            # month_emp = (month_emp[0], month_emp[1].split(' ')[:1][0].strip()[:3])
            match_join = \
                list(filter(lambda d: d['l_month'] == month_emp[1].split(' ')[:1][0].strip()[:3], month_join))[0][
                    'count']
            match_resign = \
                list(filter(lambda d: d['l_month'] == month_emp[1].split(' ')[:1][0].strip()[:3], month_resign))[0][
                    'count']
            month_avg = (month_emp[0] + match_join - match_resign + month_emp[0]) / 2
            attrition_rate = (match_resign / month_avg) * 100 if month_avg != 0 else 0
            vals = {
                # 'month': month_emp[1].split(' ')[:1][0].strip()[:3] + ' ' + month_emp[1].split(' ')[-1:][0],
                'month': month_emp[1].split(' ')[:1][0].strip()[:3],
                'attrition_rate': round(float(attrition_rate), 2)
            }
            month_attrition.append(vals)


        return month_attrition


class BroadFactor(models.Model):
    _inherit = 'hr.leave.type'

    emp_broad_factor = fields.Boolean(string="Broad Factor", help="If check it will display in broad factor type")
