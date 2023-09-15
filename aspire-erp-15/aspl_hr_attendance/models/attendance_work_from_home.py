# -*- coding: utf-8 -*-

from __future__ import division
import logging
import datetime
from odoo import api, models, _, fields, exceptions, _
from datetime import datetime, time
from odoo.exceptions import AccessError,UserError, ValidationError
from odoo.tools import format_datetime

_logger = logging.getLogger(__name__)


class AttendanceWorkFromHome(models.Model):
    _name = 'attendance.work.from.home'
    _description = "Attendances for WFH"
    _inherit = 'mail.thread'

    def _default_employee(self):
        return self.env.user.employee_id

    def _record_name(self):
        for record in self:
            name = record.employee_id.name
            start_date = record.start_date
            date = start_date.date()
            name_with_date = str(name) + " " + "WFH" + " on " + str(date)
            record.name = name_with_date

    @api.depends('start_date', 'end_date')
    def _compute_total_time(self):
        for wfh in self:
            if wfh.end_date and wfh.start_date:
                delta = wfh.end_date - wfh.start_date
                wfh.total_time = delta.total_seconds() / 3600.0
            else:
                wfh.total_time = False

    def _get_logged_in_user(self):
        for record in self:
            if record.user_id.id == self.env.user.id:
                record.logged_in_user = True
            else:
                record.logged_in_user = False

    name = fields.Char(compute='_record_name', string='Name')
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
                                  ondelete='cascade', index=True)
    start_date = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
    end_date = fields.Datetime(string="Check Out", required=True)
    flag = fields.Boolean(default=False)
    record_status = fields.Boolean('Record Status')
    work_summary = fields.Html("Work Summary", required=True)
    work_state = fields.Selection([('new', 'New'),
                                   ('to_submit', 'Submitted'),
                                   ('approved', 'Approved'),
                                   ('considered', 'Considered'),
                                   ('rejected', 'Rejected')], 'Status', readonly=True, default='new')
    user_id = fields.Many2one(related='employee_id.user_id', string='User',
                              store=True)
    total_time = fields.Float(string='Duration', compute='_compute_total_time', store=True, readonly=True)
    logged_in_user = fields.Boolean(compute='_get_logged_in_user', readonly=True)
    attendance_id = fields.Many2one('hr.attendance', string="Attendance")
    v9_attendance_id = fields.Integer()

    @api.constrains('start_date', 'end_date')
    def _check_validity_start_date_end_date(self):
        """ verifies if end_date is earlier than start_date. """
        for wfh in self:
            if wfh.start_date and wfh.end_date:
                today = datetime.now().date()
                start_date_field = wfh.start_date.date()
                if wfh.start_date.date() > datetime.now().date():
                    raise exceptions.ValidationError(_('A Work From Home entry can''t be made for a future date.'))

                if wfh.end_date < wfh.start_date:
                    raise exceptions.ValidationError(_('"Check Out" time cannot be earlier than "Check In" time.'))

    # def create(self, vals):
    #
    #     userObj = self.env['hr.employee'].search([('id', '=', vals['employee_id'])])
    #     attenDataObj = self.search([('user_id', '=', userObj.user_id.id)])
    #
    #     if not vals['end_date'] > vals['start_date']:
    #         raise Warning(_('End time must be greater than start time..'))
    #
    #     for record in attenDataObj:
    #         if datetime.strptime(vals['start_date'], DEFAULT_SERVER_DATETIME_FORMAT) < datetime.strptime(
    #                 record.end_date, DEFAULT_SERVER_DATETIME_FORMAT) and datetime.strptime(vals['start_date'],
    #                                                                                        DEFAULT_SERVER_DATETIME_FORMAT) > datetime.strptime(
    #             record.start_date, DEFAULT_SERVER_DATETIME_FORMAT):
    #             raise Warning(_('Overlapped timings!! Kindly check your previous entries for the day.'))
    #
    #         if datetime.strptime(vals['end_date'], DEFAULT_SERVER_DATETIME_FORMAT) > datetime.strptime(
    #                 record.start_date, DEFAULT_SERVER_DATETIME_FORMAT) and datetime.strptime(record.end_date,
    #                                                                                          DEFAULT_SERVER_DATETIME_FORMAT) > datetime.strptime(
    #             vals['end_date'], DEFAULT_SERVER_DATETIME_FORMAT):
    #             raise Warning(_('Overlapped timings!! Kindly check your previous entries for the day.'))
    #
    #         if datetime.strptime(vals['start_date'], DEFAULT_SERVER_DATETIME_FORMAT) < datetime.strptime(
    #                 record.start_date, DEFAULT_SERVER_DATETIME_FORMAT):
    #             if datetime.strptime(vals['end_date'], DEFAULT_SERVER_DATETIME_FORMAT) > datetime.strptime(
    #                     record.start_date, DEFAULT_SERVER_DATETIME_FORMAT):
    #                 raise Warning(_('Overlapped timings!! Kindly check your previous entries for the day.'))
    #
    #     deltas = datetime.strptime(vals['start_date'], '%Y-%m-%d %H:%M:%S') - datetime.strptime(vals['end_date'],
    #                                                                                             '%Y-%m-%d %H:%M:%S')
    #     days, seconds = deltas.days, deltas.seconds
    #     hours = (days * 24 + seconds / 3600) * -1
    #     if hours > 24:
    #         raise Warning(_('Time duration exceeds 24 hours. Make sure you have selected correct time..'))
    #     return super(AttendanceWorkFromHome, self).create(vals)

    @api.model
    def create(self,vals):
        employee_id = self.env['hr.employee'].search([('id','=',vals['employee_id'])])
        if employee_id and not employee_id.permanent_work_from_home:
            if type(vals['start_date']) == str:
                start_date = datetime.strptime(vals['start_date'], '%Y-%m-%d %H:%M:%S').date()
            else:
                start_date = vals['start_date']
            wfhApplication = self.env['application.work.from.home'].search([('employee_id','=',vals['employee_id']),
                                                                            ('start_date','<=',start_date),
                                                                            ('end_date','>=',start_date),
                                                                            ('work_state','=','approved')])
        
            if not wfhApplication:
                raise ValidationError('"Work From Home" can be applied only if it is priorly approved. Please check if your "Work From Home Application" is approved.')
        return super(AttendanceWorkFromHome, self).create(vals)


    def submit_work_from_home(self):
        """ submit work from home attendance """
        for record in self:
            deltas = datetime.strptime(str(record.start_date), '%Y-%m-%d %H:%M:%S') - datetime.strptime(
                str(record.end_date),
                '%Y-%m-%d %H:%M:%S')
            days, seconds = deltas.days, deltas.seconds
            hours = (days * 24 + seconds / 3600) * -1
            if hours > 24:
                raise exceptions.ValidationError(
                    _('Time duration exceeds 24 hours. Make sure you have selected correct time..'))
            if self.end_date and self.work_summary:
                self.write({'work_state': 'to_submit'})

            mail_cc_list = []

            attendance_manager_group_users = self.env['res.users'].search([('groups_id','=',self.env.ref('hr_attendance.group_hr_attendance_manager').sudo().id)])
            hr_employee = self.env['hr.employee'].search([('user_id','in',attendance_manager_group_users.ids),('department_id.name','=','Human Resource'),('user_id.company_ids','in',record.employee_id.company_id.id)])
            for mail in hr_employee : mail_cc_list.append(mail.work_email)
            mail_cc = ','.join(mail_cc_list)
            
            url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            menuId = self.env.ref('aspl_hr_attendance.attendance_work_from_home_menu').sudo().id
            actionId = self.env.ref('aspl_hr_attendance.action_attendance_work_from_home_view').sudo().id

            approvePageURL = url + '/web#id='+ str(self.id)+ '&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=attendance.work.from.home&view_type=form'
            context = {
                        'mail_to':self.employee_id.parent_id.work_email,
                        'mail_cc':mail_cc,
                        'approvePageURL':approvePageURL,
                        'total_time':format(self.total_time,".2f") 
                    }
            
            template_id = self.env['mail.template'].sudo().search([('name','=','Work From Home of Employee')])
            mail_id = template_id.with_context(context).send_mail(self.id,force_send = True)

    def mail_to_employee_approver(self):
        mail_cc_list = []

        attendance_manager_group_users = self.env['res.users'].search([('groups_id','=',self.env.ref('hr_attendance.group_hr_attendance_manager').sudo().id)])
        hr_employee = self.env['hr.employee'].search([('user_id','in',attendance_manager_group_users.ids),('department_id.name','=','Human Resource'),('user_id.company_ids','in',self.employee_id.company_id.id)])
        for mail in hr_employee : mail_cc_list.append(mail.work_email)
        mail_cc = ','.join(mail_cc_list)
        
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menuId = self.env.ref('aspl_hr_attendance.attendance_work_from_home_menu').sudo().id
        actionId = self.env.ref('aspl_hr_attendance.action_attendance_work_from_home_view').sudo().id

        approvePageURL = url + '/web#id='+ str(self.id)+ '&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=attendance.work.from.home&view_type=form'
        context = {
                    'mail_to':self.employee_id.work_email,
                    'mail_cc':mail_cc,
                    'approvePageURL':approvePageURL,
                    'total_time':format(self.total_time,".2f")
                }
        template_id = self.env['mail.template'].sudo().search([('name','=','Approve/Reject of Work From Home')])
        mail_id = template_id.with_context(context).send_mail(self.id,force_send = True)
    
    def approve(self):
        self.write({'work_state': 'approved'})
        for rec in self:
            if rec.user_id.id == self.env.user.id:
                raise exceptions.ValidationError(
                    _('Can not approve own Attendance.'))
            else:
                hr_attendance_obj = self.env['hr.attendance']
                attendance_id = hr_attendance_obj.create({
                    'check_in': self.start_date,
                    'check_out': self.end_date,
                    'employee_id': self.employee_id.id,
                    'atten_status': False,
                })
                self.write({'work_state': 'considered',
                            'record_status': True,
                            'attendance_id': attendance_id.id})
                
                rec.mail_to_employee_approver()
        return True

    def auto_approve_attnedance_work_from_home_schedular(self):
        permenent_wfh_employee = self.env['hr.employee'].search([('with_organization','=',True),('permanent_work_from_home','=',True)])
        if permenent_wfh_employee:
            permenent_wfh_list =self.env['attendance.work.from.home'].search([('work_state','=','to_submit'),
                                                                            ('employee_id','in',permenent_wfh_employee.ids),
                                                                            ('attendance_id','=',False)])     
            for wfh in permenent_wfh_list:
                last_attendance_before_check_in = self.env['hr.attendance'].search([
                    ('employee_id', '=', wfh.employee_id.id),
                    ('check_in', '<=', wfh.start_date)
                ], order='check_in desc', limit=1)

                _logger.info("last_attendance_before_check_in == %s",last_attendance_before_check_in)
                errorMessage = []
                if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > wfh.start_date:
                    errorMessage = "Cannot create new attendance record as you were already checked in on " + format_datetime(self.env, wfh.start_date, dt_format=False)
                    wfh.message_post(body=errorMessage)
                    wfh.write({'work_state': 'rejected'})
                else:    
                    attendance_id = self.env['hr.attendance'].create({
                        'check_in': wfh.start_date,
                        'check_out': wfh.end_date,
                        'employee_id': wfh.employee_id.id,
                        'atten_status': False,
                    })
                    if attendance_id:
                        wfh.write({'work_state': 'considered',
                                    'record_status': True,
                                    'attendance_id': attendance_id.id})

                _logger.info("errorMessage == %s",errorMessage)

    # Todo: Need to fix after Attendance modification
    # def update_monthly_summary(self, cr, uid, date_object,emp_id, context=None):
    # 	if date_object:
    # 		updateSql = 'UPDATE public.attendance_daily_summary SET "dailySumm_status"= False WHERE EXTRACT(MONTH FROM date)=' + str(datetime.strptime(date_object, DEFAULT_SERVER_DATETIME_FORMAT).month) + ' and EXTRACT(YEAR FROM date) = ' + str(datetime.strptime(date_object, DEFAULT_SERVER_DATETIME_FORMAT).year) + ' and emp_id = '+  str(emp_id) + ';'
    # 		cr.execute(updateSql)

    # 		deleteSql = 'DELETE FROM public.attendance_monthly_summary WHERE EXTRACT(MONTH FROM month) = ' + str(datetime.strptime(date_object, DEFAULT_SERVER_DATETIME_FORMAT).month) +  ' and EXTRACT(YEAR FROM month) = ' + str(datetime.strptime(date_object, DEFAULT_SERVER_DATETIME_FORMAT).year)  + ' and employee = ' + str(emp_id) + ';'

    # 		cr.execute(deleteSql)

    # 		self.pool.get('attendance.monthly.summary').attendance_monthly_summary_scheduler(cr,uid,file_ids=None,context=None)

    # def update_daily_summary(self, cr, uid, date_object,emp_id, context=None):
    # 	hrAttend = self.pool.get('hr.attendance')
    # 	yesterday = datetime.strptime(date_object, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days = 1)
    # 	yesterday_beginning = datetime(yesterday.year, yesterday.month, yesterday.day,0,0,0,0)
    # 	yb = yesterday_beginning.strftime("%Y-%m-%d %H:%M:%S")
    # 	today = datetime.strptime(date_object, DEFAULT_SERVER_DATETIME_FORMAT)
    # 	today_beginning = datetime(today.year, today.month, today.day,0,0,0,0)
    # 	tb = today_beginning.strftime("%Y-%m-%d %H:%M:%S")

    # 	hrAttendSerchDateObj =  hrAttend.search(cr,uid,[('employee_id','=',emp_id),('name','>=',tb),('name','<',yb)],order="name asc",context=context)
    # 	hrAttendDataDateObj = hrAttend.browse(cr,uid,hrAttendSerchDateObj,context=context)
    # 	if hrAttendDataDateObj:
    # 		updateSql ='UPDATE public.hr_attendance SET atten_status = False WHERE id in' + str(hrAttendSerchDateObj).replace("[", "(").replace("]", ")") +';'
    # 		cr.execute(updateSql)

    # 		attenRecSumObj = self.pool.get('attendance.daily_summary')
    # 		attenRecSumId = attenRecSumObj.search(cr,uid,[('emp_id','=',emp_id),('date','=',today_beginning.date())])
    # 		attenRecSumData = attenRecSumObj.browse(cr,uid,attenRecSumId).unlink()

    # 		self.pool.get('attendance.daily_summary').attendance_daily_summary_scheduler(cr,uid,context=None)

    def set_to_default(self):
        self.write({'work_state': 'new'})
        return True

    def reject(self):
        """ reject work from home attendance """
        if self.attendance_id:
            self.attendance_id.unlink()
            self.write({'work_state': 'rejected'})
            self.mail_to_employee_approver()
        else:
            raise exceptions.ValidationError(_('Related Attendance does not exists'))
        return True

    # def createEmpTimeSheetRecord(self, dateObj, typeObj, emp_id, action_desc):
    #     """ create hr attendance record """
    #
    #     attenRecordObj = self.env['hr.attendance']
    #     dateTimeObj = datetime.today()
    #     try:
    #         today = dateTimeObj.strftime(DEFAULT_SERVER_DATE_FORMAT)
    #         datetime_object = datetime.strptime(dateObj, DEFAULT_SERVER_DATETIME_FORMAT)
    #         date = datetime_object.strftime(DEFAULT_SERVER_DATE_FORMAT)
    #         date_object = datetime_object.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    #         DatE = date_object
    #
    #         hrObj = self.env['hr.employee'].search([('id', '=', emp_id)])
    #         # hrDataObj = hrObj.browse(cr, uid, [emp_id], context=context)
    #
    #         if hrObj.name:
    #             name = hrObj.name
    #             nameObj = str(name) + " " + "on" + " " + str(date)
    #
    #             attenRecordObj.create({
    #                 'name': date_object,
    #                 'employee_id': emp_id,
    #                 'atten_status': False,
    #                 'action': typeObj,
    #                 'action_desc': action_desc,
    #             })
    #     except ValidationError as error:
    #
    #         if str(error) in "(u'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', None)":
    #             pass
    #         else:
    #             _logger.error(str(error))
    #             status = False
    #             # update work from home status is failure
    #             self.updateWorkFromHomeRecordStatus(status)
    #
    #
    #     except Exception as e:
    #         _logger.error('Something is wrong')
    #         _logger.error(str(e))
    #         status = False
    #         # update work from home status is failure
    #         self.updateWorkFromHomeRecordStatus(status)

    # def updateWorkFromHomeRecordStatus(self, status):
    #     """ update work from home record status """
    #     try:
    #         if status:
    #             self.write({'record_status': status})
    #     except Exception as e:
    #         _logger.error('Something is wrong')
    #         _logger.error(str(e))

    # Approve work from home notification scheduler
    def approve_work_from_home_notification_scheduler(self):
        attenWorFroHomeObj = self.search([('work_state', 'in', ['to_submit'])])
        # Send mail to Parent for approve leave
        # Todo Need to fix 20-12-2021 Commented by RPJ
        # try:
        #     for record in attenWorFroHomeObj:
        #         template = self.pool.get('ir.model.data').get_object(cr, uid, 'hr_attendance_aspire',
        #                                                              'approve_work_base_home_notify')
        #         mail_id = self.pool.get('mail.template').send_mail(cr, uid, template.id, record.id, force_send=True)
        # except Exception as e:
        #     _logger.error('Email not send')
        #     _logger.error(str(e))
        return True

    def unlink(self):
        for record in self:
            if record.work_state in ['approved', 'considered']:
                raise exceptions.ValidationError(_('Approved or Considered records cannot be deleted'))
        return super(AttendanceWorkFromHome, self).unlink()

    @api.model
    def action_approve_wfh(self):
        for wfh in self:
            if wfh.work_state == 'to_submit':
                wfh.approve()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
