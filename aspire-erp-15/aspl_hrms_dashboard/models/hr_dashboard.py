from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.http import request

class Employee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def check_user_group_hr(self):
        uid = request.session.uid
        user = self.env['res.users'].sudo().search([('id', '=', uid)], limit=1)

        if user.has_group('hr_recruitment.group_hr_recruitment_manager'):
            return "main_hr"
        elif user.has_group('hr_recruitment.group_hr_recruitment_user'):
            return "jr_hr"
        else:
            return False
        
    @api.model
    def get_user_employee_details_hr(self):
        if ( Employee.check_user_group_hr(self) == False ):
            return False
        else:
            uid = request.session.uid
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', uid)], limit=1)
            cookies = request.httprequest.cookies.get('cids').split(',')
            
            active_compnys = []
            for i in cookies:
                active_compnys.append(self.env['res.company'].browse(int(i)).name)

            # ********************* TODAY TIME OFF TABLE ********************* #
            today_time_off_emp = []

            for i in self.env['hr.leave'].sudo().search([
                ('date_from'[:10],'<=',datetime.now().strftime("%Y-%m-%d")),
                ('date_to'[:10],'>=',datetime.now().strftime("%Y-%m-%d")),
                ('state', '=', 'validate'),
            ]):
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

            if employee :
                data = {
                    'today_time_off_emp' : today_time_off_emp,
                    'upcoming_events' : upcoming_events,
                }
                return data
            else:
                return False
