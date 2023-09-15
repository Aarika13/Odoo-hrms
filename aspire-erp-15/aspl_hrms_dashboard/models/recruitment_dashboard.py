from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.http import request

class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def check_user_group_recruitment(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)

        if user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            return "main_hr"
        elif user.has_group('hr_recruitment.group_hr_recruitment_user'):
            return "jr_hr"
        else:
            return False
        


    @api.model
    def get_user_employee_details_recruitment(self):
        if ( Employee.check_user_group_recruitment(self) == False ):
            return False
        else:
            uid = request.session.uid
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1)
            cookies = request.httprequest.cookies.get('cids').split(',')
            
            active_compnys = []
            for i in cookies:
                active_compnys.append(self.env['res.company'].browse(int(i)).name)

            # ********************* TABLE OF RECRUITMENT ********************* #
            loop = []
            stages = []
            dict = {}

            if ( Employee.check_user_group_recruitment(self) == "main_hr" ):
                for i in self.env['job.opening'].sudo().search([
                    ('active','=',True),
                    ('state','=','recruit'),
                    ('company_id','in',active_compnys),
                ]):
                    loop.append(i.name)
                
            elif ( Employee.check_user_group_recruitment(self) == "jr_hr" ):
                for i in self.env['job.opening'].sudo().search([
                    ('user_id', '=', uid),
                    ('active','=',True),
                    ('state','=','recruit'),
                    ('company_id','in',active_compnys),
                    ]):
                    loop.append(i.name)
                
            for i in self.env['hr.recruitment.stage'].sudo().search([]):
                stages.append(i.name)

            if ( Employee.check_user_group_recruitment(self) == "main_hr" ):
                for i in range(len(loop)):
                    dict.update({i:{0:loop[i]}})
                    for j in stages:
                        first = self.env['hr.applicant'].sudo().search_count(
                        [('active','=',True),('job_opening_id', '=', loop[i]),('stage_id','=', j)])
                        dict[i][j] = first

            elif ( Employee.check_user_group_recruitment(self) == "jr_hr" ):
                for i in range(len(loop)):
                    dict.update({i:{0:loop[i]}})
                    for j in stages:
                        first = self.env['hr.applicant'].sudo().search_count(
                        [('user_id', '=', uid),('active','=',True),('job_opening_id', '=', loop[i]),('stage_id','=', j)])
                        dict[i][j] = first
            # print("*************DICT**************",dict)
            
            # ********************* TABLE OF ACTIVITY ********************* #
            if ( Employee.check_user_group_recruitment(self) == "main_hr" ):
                users_temp = []
                activity_types_temp = []
                activity_types = []
                del_dict_index_no = []
                dict_of_activity = {}

                for i in self.env['mail.activity'].sudo().search([
                    ('res_model', '=', 'hr.applicant'),
                ]):
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
                tem=0
                for i in dict_of_activity:
                    for j in dict_of_activity[i]:
                        if type(dict_of_activity[i][j]) == int:
                            if dict_of_activity[i][j] == 0:
                                tem = 0
                            else:
                                tem = 1
                                break
                    if tem==0:
                        del_dict_index_no.append(i)
                
                for i in del_dict_index_no:
                    del dict_of_activity[i]
                # print("*************dict_of_activity**************",dict_of_activity)

            # ********************* SAPRATE ACTIVITY BOXES ********************* #
            saprate_activity_type_temp = []
            saprate_activity_type_temp_2 = ['To Do','Email','Call','Meeting']
            saprate_activity = []

            for i in self.env['mail.activity'].sudo().search([
                ('res_model', '=', 'hr.applicant'),
                ('user_id','=',uid),
                ('date_deadline','>=',datetime.now())
            ]):
                saprate_activity_type_temp.append(i.activity_type_id.name)
                for i in saprate_activity_type_temp: 
                    if i not in saprate_activity_type_temp_2 :
                        saprate_activity_type_temp_2.append(i)

            for i in saprate_activity_type_temp_2:
                temp_numeric = self.env['mail.activity'].sudo().search_count([
                    ('res_model', '=', 'hr.applicant'),
                    ('user_id','=',uid),
                    ('date_deadline','>=',datetime.now()),
                    ('activity_type_id','=',i)
                ])
                saprate_activity.append([i,temp_numeric])
            # print("*************** saprate_activity ***************",saprate_activity)

            if employee:
                if ( Employee.check_user_group_recruitment(self) == "main_hr" ):
                    data = {
                        'saprate_activity':saprate_activity,
                        'loop':dict,
                        'stages':stages,
                        'activity_types':activity_types,
                        'dict_of_activity':dict_of_activity,
                    }
                elif ( Employee.check_user_group_recruitment(self) == "jr_hr" ):
                    data = {
                        'saprate_activity':saprate_activity,
                        'loop':dict,
                        'stages':stages,
                    }
                return data
            else:
                return False

    @api.model
    def recruitment_cost_bar_chart_method(self):
        if ( Employee.check_user_group_recruitment(self) == False ):
            return False
        else:
            cookies = request.httprequest.cookies.get('cids').split(',')
            active_compnys = []
            for i in cookies:
                active_compnys.append(self.env['res.company'].browse(int(i)).name)

            recruitment_cost = []
            for i in self.env['job.opening'].sudo().search([
                        ('active','=',True),
                        ('company_id','in',active_compnys),
                        ]):
                recruiter_id = self.env['hr.contract'].sudo().search([
                        ('employee_id','=',i.user_id.name),
                        ('state','=','open'),
                        ])
                if ( i.end_date == False ) :
                    recruitment_days = datetime.now() - datetime.combine(i.opened_date, datetime.min.time())
                else :
                    recruitment_days = i.end_date - i.opened_date
                recruiter_id_cost = recruitment_days.days * ( recruiter_id.wage ) / 30
                recruitment_cost.append([i.name,recruiter_id_cost])

            for i in recruitment_cost :
                interviewer_id_cost = 0
                candidates_count = 0
                for j in self.env['hr.applicant'].sudo().search([
                    ('job_opening_id','=',i[0]),
                    ]):
                        interviewer_id = self.env['hr.contract'].sudo().search([
                                ('employee_id','=',j.feedbacks_ids.interviewer_id.name),
                                ('state','=','open'),
                                ])
                        if ( j.feedbacks_ids.interview_time > 0 ) :
                            interviewer_id_cost += j.feedbacks_ids.interview_time * ( interviewer_id.wage ) / 11040
                        if ( j.stage_id.name == 'Joined' ) :
                            candidates_count += 1
                i[1] += interviewer_id_cost
                interviewer_id_cost = 0
                if( ( i[1] > 0 ) and ( candidates_count > 0 ) ) :
                    i[1] /= candidates_count
                else : 
                    i[1] = 0
                i.append(candidates_count)
                candidates_count = 0
            # print("===================== recruitment_cost ===========================",recruitment_cost)
                
            return recruitment_cost