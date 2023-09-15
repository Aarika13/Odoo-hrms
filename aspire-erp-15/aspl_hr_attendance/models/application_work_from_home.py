from __future__ import division
import logging
import datetime
from odoo import api, models, _, fields, exceptions, _
from datetime import date,datetime, time,timedelta
from odoo.exceptions import AccessError
import numpy as np
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ApplicationWorkFromHome(models.Model):
    _name = 'application.work.from.home'
    _description = "Application for WFH"
    _inherit = 'mail.thread'

    def _default_employee(self):
        return self.env.user.employee_id
    
    def _record_name(self):
        for record in self:
            record.name = str(record.employee_id.name) + " " + "WFH Application" + " on " + str(record.start_date)
    
    name = fields.Char(compute='_record_name',string='Name')
    employee_id = fields.Many2one('hr.employee', string="Employee", default=_default_employee, required=True,
                                  ondelete='cascade', index=True,tracking=True)
    start_date = fields.Date(string="Start Date", default=fields.Datetime.now, required=True,tracking=True)
    end_date = fields.Date(string="End Date", required=True)

    reason = fields.Html("Reason", required=True,tracking=True)
    work_state = fields.Selection([('new', 'New'),
                                   ('to_submit', 'Submitted'),
                                   ('approved', 'Approved'),
                                   ('rejected', 'Rejected')], 'Status', readonly=True, default='new',tracking=True)
    user_id = fields.Many2one(related='employee_id.user_id', string='User',
                              store=True,tracking=True)
    
    total_day = fields.Integer("Total Days")
    type_of_wfh = fields.Selection([('planned_wfh','Planned'),('unplanned_wfh','Unplanned')],string="Application Type",required=True,tracking=True)
    logged_in_user = fields.Boolean(compute='_get_logged_in_user', readonly=True,tracking=True)

    @api.constrains('start_date', 'end_date')
    def _check_validity_start_date_end_date(self):
        """ verifies if end_date is earlier than start_date. """
        for wfh in self:
            if wfh.start_date and wfh.end_date:
                today = datetime.today()

                if wfh.end_date < wfh.start_date:
                    raise exceptions.ValidationError(_('"End Date" cannot be earlier than "Start Date" time.'))
    
    def _get_logged_in_user(self):
        for record in self:
            if record.user_id.id == self.env.user.id:
                record.logged_in_user = True
            else:
                record.logged_in_user = False

    @api.onchange('start_date', 'end_date')
    def _compute_total_day(self):
        for wfh in self: 
            if wfh.end_date and wfh.start_date:
                domain = [
                    ('date_from', '>=', wfh.start_date),
                    ('date_from', '<=', wfh.end_date),
                    ('resource_id' , '=', wfh.employee_id.resource_id.id),
                ]
                n_holidays = self.env['resource.calendar.leaves'].search(domain)
                
                total_count = np.busday_count(wfh.start_date,wfh.end_date)
                _logger.info("Holiday == %s Total_count == %s ",n_holidays,total_count)
                wfh.total_day = (total_count +1) - len(n_holidays)
                
            else:
                wfh.total_day = False
    
    def submit_application_work_from_home(self):
        for record in self:
            if record.end_date and record.reason:
                record.write({'work_state': 'to_submit'})

            mail_cc_list = []

            attendance_manager_group_users = self.env['res.users'].search([('groups_id','=',self.env.ref('hr_attendance.group_hr_attendance_manager').sudo().id)])
            hr_employee = self.env['hr.employee'].search([('user_id','in',attendance_manager_group_users.ids),('department_id.name','=','Human Resource'),('user_id.company_ids','in',record.employee_id.company_id.id)])
            for mail in hr_employee : mail_cc_list.append(mail.work_email)
            mail_cc = ','.join(mail_cc_list)
            
            url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            menuId = self.env.ref('aspl_hr_attendance.application_work_from_home_view_data').sudo().id
            actionId = self.env.ref('aspl_hr_attendance.action_application_work_from_home_view').sudo().id

            approvePageURL = url + '/web#id='+ str(record.id)+ '&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=application.work.from.home&view_type=form'
            context = {
                        'mail_to':record.employee_id.parent_id.work_email,
                        'mail_cc':mail_cc,
                        'approvePageURL':approvePageURL,
                    }
            _logger.info("Context: %s", context)
            template_id = self.env['mail.template'].sudo().search([('name','=','Application Of Work From Home')])
            mail_id = template_id.with_context(context).send_mail(record.id,force_send = True) 

    def mail_to_employee_approver(self):
        mail_cc_list = []

        attendance_manager_group_users = self.env['res.users'].search([('groups_id','=',self.env.ref('hr_attendance.group_hr_attendance_manager').sudo().id)])
        hr_employee = self.env['hr.employee'].search([('user_id','in',attendance_manager_group_users.ids),('department_id.name','=','Human Resource'),('user_id.company_ids','in',self.employee_id.company_id.id)])
        for mail in hr_employee : mail_cc_list.append(mail.work_email)
        mail_cc = ','.join(mail_cc_list)
        
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menuId = self.env.ref('aspl_hr_attendance.application_work_from_home_view_data').sudo().id
        actionId = self.env.ref('aspl_hr_attendance.action_application_work_from_home_view').sudo().id

        approvePageURL = url + '/web#id='+ str(self.id)+ '&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=application.work.from.home&view_type=form'
        context = {
                    'mail_to':self.employee_id.work_email,
                    'mail_cc':mail_cc,
                    'approvePageURL':approvePageURL,
                }
        template_id = self.env['mail.template'].sudo().search([('name','=','Approve/Reject of Application Of Work From Home')])
        mail_id = template_id.with_context(context).send_mail(self.id,force_send = True)

    def application_approve(self):
        for rec in self:
            if rec.user_id.id == self.env.user.id:
                raise exceptions.ValidationError(
                    _('Can not approve own WFH Application'))
            else:
                rec.write({'work_state': 'approved'})
                rec.mail_to_employee_approver()         
        return True
    
    def application_reject(self):
        self.write({'work_state': 'rejected'})
        self.mail_to_employee_approver()
        return True
    
    def application_set_to_default(self):
        self.write({'work_state': 'new'})
        return True

    @api.model
    def create(self,vals):
        if type(vals['start_date']) == str:
            start_date = datetime.strptime(vals['start_date'], '%Y-%m-%d').date()
        else:
            start_date = vals['start_date']
        if (vals['type_of_wfh'] == 'planned_wfh') and (start_date == date.today() or start_date <= date.today()):
            raise ValidationError('Planned Work From Home must be applied before a day.')

        return super(ApplicationWorkFromHome, self).create(vals)
    
    def unlink(self):
        for record in self:
            if record.work_state in ['approved', 'rejected']:
                raise exceptions.ValidationError(_('Approved or Rejected records cannot be deleted'))
        return super(ApplicationWorkFromHome, self).unlink()
