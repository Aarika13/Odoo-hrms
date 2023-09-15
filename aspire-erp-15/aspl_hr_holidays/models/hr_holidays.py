# -*- coding: utf-8 -*-
import logging
import pandas as pd
from odoo import models, fields, api, _, tools
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from dateutil import parser
from ..constant.constant import Constant
from odoo.exceptions import ValidationError, UserError
from odoo.exceptions import AccessError
from pytz import timezone

_logger = logging.getLogger(__name__)

ALLOCATE_REASON = [
    ('compensation', 'Compensation'),
]
INTERVAL = [
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'),
]


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    _description = "Leave Type"

    # Override get days function
    # def get_days(self, employee_id):
    #     result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
    #                             virtual_remaining_leaves=0)) for id in self.ids)
    #     domain = [('employee_id', '=', employee_id), ('state', 'in', ['confirm', 'validate1', 'validate']),
    #               ('holiday_status_id', 'in', self.ids)]
    #     holiday_ids = self.pool['hr.holidays'].search(domain)
    #     for holiday in self.pool['hr.holidays'].browse(holiday_ids):
    #         status_dict = result[holiday.holiday_status_id.id]
    #         if holiday.type == 'add' or holiday.type == 'carry_forward':
    #             status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
    #             if holiday.state == 'validate':
    #                 status_dict['max_leaves'] += holiday.number_of_days_temp
    #                 status_dict['remaining_leaves'] += holiday.number_of_days_temp
    #         elif holiday.type == 'remove' or holiday.type == 'lapsed':  # number of days is negative
    #             status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
    #             if holiday.state == 'validate':
    #                 status_dict['leaves_taken'] += holiday.number_of_days_temp
    #                 status_dict['remaining_leaves'] -= holiday.number_of_days_temp
    #     return result

    sequence = fields.Integer(string='Sequence', help="Gives the sequence order when displaying a list of state.")
    no_leave = fields.Integer(string='No Of Leaves', help="No Of Leaves To Add")
    add_interval = fields.Selection(INTERVAL, string='Interval')
    no_days = fields.Integer(string='No Of Days')
    allow_in_notice = fields.Boolean(string='Allow in notice period')
    limit = fields.Boolean('Allow to Override Limit', help='If you select this check box,'
                                                           'the system allows the employees to take more leaves than '
                                                           'the available ones for this type and will not take them '
                                                           'into account for the "Remaining Legal Leaves" '
                                                           'defined on the employee form.')

    employee_id = fields.Many2one("hr.employee")
    # def name_get(self):
    #     if self._context is None:
    #         context = {}
    #     if not self._context.get('employee_id', False):
    #         # leave counts is based on employee_id, would be inaccurate if not based on correct employee
    #         return super(HrLeaveType, self).name_get()
    #     res = []
    #     for record in self:
    #         name = record.name
    #         if not record.limit:
    #             name = name + ('  (%g)' % (record.remaining_leaves or 0.0))
    #         res.append((record.id, name))
    #     return res


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'
    _description = "Leave Allocation"

    # @api.onchange('holiday_status_id')
    # def onchange_holiday_status_id(self):
    #     result = {'value': {}}
    #     if self.holiday_status_id.id:
    #         holiday_sequence = self.env['hr.leave.type'].browse(self.holiday_status_id.id)
    #         result['value']['sequence'] = holiday_sequence.sequence
    #     return result

    # payslip_status = fields.Boolean(string='Reported in last payslips',
    #             help='Green this button when the leave has been taken into account in the payslip.')
    # type = fields.Selection(
    #     [('remove', 'Removed'), ('add', 'Added'), ('lapsed', 'Lapsed Leave'), ('carry_forward', 'Carry Forward')],
    #     'Request Type', required=True, readonly=True,
    #     states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
    #     help="Choose 'Leave Request' if someone wants to take an off-day. \n"
    #          "Choose 'Allocation Request' if you want to increase the number of leaves available for someone",
    #     select=True)
    # forward_to = fields.Many2one('hr.employee', "Forwarded To", readonly=True,
    #                              domain=[('with_organization', '=', True)])
    granted_date = fields.Datetime('Date', default=datetime.now(),
                                   states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    # month_start = fields.Datetime(compute='_compute_month_start', string='Month Start')
    adjust_planned_leave = fields.Boolean('Adjust planned leave with unplanned leave')
    # month_end = fields.Datetime(compute='_compute_month_end', string='Month End')
    carry_leave = fields.Boolean('Carry forward leave', default=False)
    type = fields.Selection(
        [('remove', 'Removed'), ('add', 'Added'), ('lapsed', 'Lapsed Leave'), ('carry_forward', 'Carry Forward')],
        'Request Type', readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="Choose 'Leave Request' if someone wants to take an off-day. \n"
             "Choose 'Allocation Request' if you want to increase the number of leaves available for someone",
        select=True)
    allocation_id = fields.Integer()

    # TODO : Need to Comment or Remove after Leave Script.
    # _sql_constraints = [
    #     ('duration_check',
    #      "CHECK( (allocation_type='regular') or (allocation_type != 'regular'))",
    #      "The duration must be greater than 0."),
    # ]

    # Get month start date
    def _compute_month_start(self):
        dates = datetime.now().date()
        month = dates.month
        year = dates.year
        if month == 1:
            month = 12
            year = year - 1
        else:
            month = month - 1
            year = year
        prev_month_start_date = datetime.date(year, month, 1)
        res = {}
        for record in self.browse(self.ids):
            res[record.id] = prev_month_start_date.strftime("%Y-%m-%d")
        return res

    # Get month end date
    def _compute_month_end(self):
        dates = datetime.now().date()
        month = dates.month
        year = dates.year
        start_date = datetime.date(year, month, 1)
        # if month == 12:
        #     month = 1
        #     year = year+1
        # else:
        #     month = month+1
        #     year = year
        prev_month_end_date = start_date - timedelta(days=1)
        res = {}
        for record in self.browse(self.ids):
            res[record.id] = prev_month_end_date.strftime("%Y-%m-%d")
        return res

    # Add leaves schedular
    @api.model
    def leave_schedular(self):
        # Carry forwarded leave after year 2016 and month is first
        current_month = datetime.now().month
        current_year = datetime.now().year
        try:
            if current_month == 1:
                leave_forwarded = self.leaves_forward_new_policy()
        except Exception as e:
            _logger.error('Something 1 is wrong')
            _logger.error(str(e))
        # Add employee leave as per monthly and yearly in leave types
        try:
            leave_type_ids = self.env['hr.leave.type'].search([('active', '=', 'True')])
            for record in self.env['hr.leave.type'].browse(leave_type_ids.ids):
                if record.add_interval and record.no_leave:
                    if record.add_interval == 'yearly':
                        if current_month != 1:
                            continue
                    add_leave = self.add_leave(record)
                else:
                    continue
        except Exception as e:
            _logger.error('Something 2 is wrong')
            _logger.error(str(e))
        return True

    # Add leave function for all leave type
    def add_leave(self, record):
        try:
            current_year = datetime.now().year
            employee_obj = self.env['hr.employee']
            leave_type_obj = self.env['hr.leave.type']
            holidays_obj = self.env['hr.leave.allocation']

            # Calculate Month start and end date
            today = datetime.today().date()
            dates = datetime.now()
            month = dates.month
            year = dates.year
            month_start = today.replace(day=1).strftime("%Y-%m-%d")
            year_end = date(year, 12, 31)
            if month == 12:
                month = 1
                year = year + 1
            else:
                month = month + 1
                year = year
            # month_end = datetime.date(year + int(month/12), (month % 12+1), 1)-timedelta(days=1).strftime("%Y-%m-%d")
            month_end = pd.Period(today, freq='M').end_time.date().strftime("%Y-%m-%d")
            # If record then add leaves
            if record:
                add_leave = record.no_leave  # Add leave no in leave types
                emp_ids = employee_obj.search([('with_organization', '=', True)])
                leave_ids = []
                for emp in employee_obj.browse(emp_ids.ids):
                    add_leave = record.no_leave
                    if emp.emp_state == 'on_notice':
                        continue
                    if emp.emp_state == 'training':
                        continue
                    if emp.emp_state == 'new':
                        continue
                    if emp.emp_state == 'probation' and record.name in ["Unplanned Leaves", "Floating Holiday",
                                                                        "Maternity Leaves"]:
                        continue
                    if emp.with_organization == False:
                        continue
                    # Check current month leave is added or not
                    domain = [('employee_id', '=', emp.id,), ('type', '=', 'add'), ('granted_date', '>=', month_start),
                              ('granted_date', '<=', month_end), ('holiday_status_id', '=', record.id)]
                    is_added = holidays_obj.search(domain)
                    # Continue if leave is added for current month
                    if is_added:
                        continue
                    # End check process of employee leave is add or not
                    vals = {
                        'name': _('Leave Granted to %s') % emp.name,
                        'state': 'validate',
                        'employee_ids': emp.ids,
                        'employee_id': emp.id,
                        'holiday_status_id': record.id,
                        'type': 'add',
                        'holiday_type': 'employee',
                        'number_of_days': add_leave,
                        'adjust_planned_leave': False
                    }
                    # if record.sequence == 1:
                    #     vals['date_to'] = month_end
                    # elif record.sequence in (2, 3):
                    #     vals['date_to'] = year_end
                    leave_ids.append(holidays_obj.create(vals))
                    # Approve leave request
                # for leave_id in leave_ids:
                #     for sig in ('confirm', 'validate', 'second_validate'):
                #         self.signal_workflow(cr, uid, [leave_id], sig)

                # Send Mail to hr when run schedular
                try:
                    # template = self.env['ir.model.data'].get_object('aspl_hr_holidays', 'run_schedular')
                    search_domain = [('name', '=', 'Leave Schedular')]
                    template_id = self.env['mail.template'].search(search_domain)
                    template_id.send_mail(record.id, force_send=True)
                    # search_domain = [('name', '=', 'Leave Schedular')]
                    # template_id = self.env['mail.template'].search(search_domain)
                    # template_id.send_mail(template_id.id, record.id, force_send=True)
                    # compose_id = self.env['mail.compose.message'].create({
                    #     'model': 'hr.leave',
                    #     'composition_mode': 'mass_mail',
                    #     'template_id': template_id.id,
                    #     'notify': True,
                    # })
                    # mail_values = {
                    #     'model': 'hr.leave',
                    #     'template_id': template_id.id,
                    #     'notify': True,
                    # }
                    # compose_id._action_send_mail(compose_id.id)
                    # self.env['mail.mail'].create(mail_values).send()

                except Exception as e:
                    _logger.error('Email not send')
                    _logger.error(str(e))
                # End send mail schedular

        except Exception as e:
            _logger.error('Something 3 is wrong')
            _logger.error(str(e))
        return True

    # Leave forward as per new policy
    def leaves_forward_new_policy(self):
        employee_obj = self.env['hr.employee']
        emp_ids = employee_obj.search([])   # ('with_organization', '=', 'True')
        try:
            leave_type_obj = self.env['hr.leave.type'].search(
                [('name', 'in', ('Planned leave', 'Unplanned Leaves', 'Floating Holiday'))]
            )
            leave_dict = leave_type_obj.get_employees_days(emp_ids.ids)
            for emp_id in emp_ids.ids:

                values = {}
                planned_leave_id = self.env['hr.leave.type'].search([
                    ('name', '=', 'Planned leave')]).id
                planned_leaves = leave_dict.get(emp_id).get(planned_leave_id).get('remaining_leaves')
                unplanned_leave_id = self.env['hr.leave.type'].search([
                    ('name', '=', 'Unplanned Leaves')]).id
                unplanned_leaves = leave_dict.get(emp_id).get(unplanned_leave_id).get('remaining_leaves')
                floating_leave_id = self.env['hr.leave.type'].search([
                    ('name', '=', 'Floating Holiday')]).id
                floating_leaves = leave_dict.get(emp_id).get(floating_leave_id).get('remaining_leaves')
                total_leave = planned_leaves + unplanned_leaves
                if total_leave <= 0:
                    continue
                if total_leave <= 24:
                    continue
                else:
                    values = calculate_leaves_new(planned_leaves, total_leave)
                new_planned = values['value']['planned_leave']
                new_unplanned = values['value']['unplanned_leave']
                lapsed_planned = planned_leaves - new_planned
                lapsed_unplanned = unplanned_leaves - new_unplanned
                if lapsed_planned != 0:
                    remove_lapsed_planned = self.add_remove_employee_leaves(emp_id, 1, lapsed_planned,
                                                                            'lapsed')
                if lapsed_unplanned != 0:
                    remove_lapsed_unplanned = self.add_remove_employee_leaves(emp_id, 2, lapsed_unplanned,
                                                                              'lapsed')
        except Exception as e:
            _logger.error('Something 4 is wrong')
            _logger.error(str(e))
        return True

    def add_remove_employee_leaves(self, ids, leave_sequence, no_of_leave, types):
        leave_type_obj = self.env['hr.leave.type']
        holidays_obj = self.env['hr.leave.allocation']
        no_of_leave = -no_of_leave
        # Holiday leave id
        leave_type_id = leave_type_obj.search([('sequence', '=', leave_sequence)])
        if not leave_type_id:
            return False
        # Name message from leave type
        if types == 'carry_forward':
            des = 'Carry forward leave from total'
        else:
            des = 'Lapsed leave from total leave'
        leave_type_id = leave_type_id and leave_type_id[0] or False
        leave_ids = []  # For add leaves
        vals = {
            'name': des,
            'type': types,
            'state': 'validate',
            'holiday_type': 'employee',
            'employee_id': ids,
            'holiday_status_id': leave_type_id.id,
            'number_of_days': no_of_leave,
            'adjust_planned_leave': False,
            'carry_leave': True,
        }
        leave_ids.append(holidays_obj.create(vals))
        # for leave_id in leave_ids:
        #     for sig in ('confirm', 'validate', 'second_validate'):
        #         self.signal_workflow([leave_id], sig)
        return True

# Approve leave notification schedular
    def approve_leave_notification_schedular(self):
        holiday_obj = self.env['hr.leave']
        domain = [('state', 'in', ['confirm']), ('carry_leave', '=', False)]
        # domain = [('state', 'in', ['confirm']), ('type', '=', 'remove'), ('carry_leave', '=', False)]
        holiday_ids = holiday_obj.search(domain)
        # Send mail to Parent for approve leave
        try:
            for record in holiday_obj.browse(holiday_ids):
                search_domain = [('name', '=', 'Leave Notification')]
                template = self.env['mail.template'].search(search_domain)
                mail_id = template.send_mail(record.id.id,force_send=True)
        except Exception as e:
            _logger.error('Email not send')
            _logger.error(str(e))
        return True


# Inherit hr.leave model
class HolidaysRequest(models.Model):
    _name = 'hr.leave'
    _description = "Time Off"
    _inherit = ['hr.leave', 'mail.thread']  # , 'ir.needaction_mixin'

    def forward_employee_leave(self):
        return {
            'name': _("Forward Employee Leave"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'forward.leave',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': '[]',
            'context': {'leave_id': self.ids[0]},
        }

    # Override method for fix time issue from calander
    def _default_get_request_parameters(self, values):
        new_values = dict(values)
        # global_from, global_to = False, False
        # # TDE FIXME: consider a mapping on several days that is not the standard
        # # calendar widget 7-19 in user's TZ is some custom input
        # if values.get('date_from'):
        #     user_tz = self.env.user.tz or 'UTC'
        #     localized_dt = timezone('UTC').localize(values['date_from']).astimezone(timezone(user_tz))
        #     global_from = localized_dt.time().hour == 7 and localized_dt.time().minute == 0
        #     new_values['request_date_from'] = localized_dt.date()
        # if values.get('date_to'):
        #     user_tz = self.env.user.tz or 'UTC'
        #     localized_dt = timezone('UTC').localize(values['date_to']).astimezone(timezone(user_tz))
        #     global_to = localized_dt.time().hour == 19 and localized_dt.time().minute == 0
        #     new_values['request_date_to'] = localized_dt.date()
        # if global_from and global_to:
        #     new_values['request_unit_custom'] = True
        return new_values

    # def _domain_leave_type(self):
    #     id_list = []
    #     group_hr_manager = self.env['res.users'].has_group('hr.group_hr_manager')
    #     group_hr_officer = self.env['res.users'].has_group('hr.group_hr_user')
    #     employeeObj = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
    #     if group_hr_officer or group_hr_manager:
    #         leaveTypeObj = self.env['hr.leave.type'].search([])
    #     else:
    #         if employeeObj and employeeObj.emp_state == 'on_notice':
    #             leaveTypeObj = self.env['hr.leave.type'].search([('allow_in_notice', '=', True)])
    #         else:
    #             leaveTypeObj = self.env['hr.leave.type'].search([])
    #     for leave_type in leaveTypeObj:
    #         id_list.append(leave_type.id)
    #     return [('id', 'in', id_list)]

    #     # _order = "type desc, date_from asc"

    #     state = fields.Selection(
    #         [('draft', 'To Submit'), ('cancel', 'Cancelled'), ('confirm', 'To Approve'), ('refuse', 'Refused'),
    #          ('validate1', 'Second Approval'), ('validate', 'Approved')],
    #         'Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
    #         help='The status is set to \'To Submit\', when a holiday request is created.\
    #     \nThe status is \'To Approve\', when holiday request is confirmed by user.\
    #     \nThe status is \'Refused\', when holiday request is refused by manager.\
    #     \nThe status is \'Approved\', when holiday request is approved by manager.')
    adjust_planned_leave = fields.Boolean('Adjust planned leave with unplanned leave')
    carry_leave = fields.Boolean('Carry forward leave', default=False)
    type = fields.Selection(
        [('remove', 'Removed'), ('add', 'Added'), ('lapsed', 'Lapsed Leave'), ('carry_forward', 'Carry Forward')],
        'Request Type', readonly=True,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="Choose 'Leave Request' if someone wants to take an off-day. \n"
             "Choose 'Allocation Request' if you want to increase the number of leaves available for someone",
        select=True)
    request_date_from_session = fields.Selection([
        ('am', 'Session 1'), ('pm', 'Session 2')],
        string="Date Session Start", default='am', tracking=True)
    request_date_to_session = fields.Selection([
        ('am', 'Session 1'), ('pm', 'Session 2')],
        string="Date Session Start", default='pm',  tracking=True)
    request_id = fields.Integer()

    @api.depends('date_from', 'date_to', 'employee_id', 'request_date_from_session', 'request_date_to_session')
    def _compute_number_of_days(self):
        for holiday in self:
            if holiday.date_from and holiday.date_to:
                if ( (holiday.date_from.strftime("%Y-%m-%d") == holiday.date_to.strftime("%Y-%m-%d")) and (self.request_date_from_session == 'pm') and (self.request_date_to_session == 'am') ):
                    raise ValidationError(_(Constant.NOT_VALID_SESSION_SAME_DAY))
                else:
                    days = holiday._get_number_of_days(holiday.date_from, holiday.date_to, holiday.employee_id.id)['days']
                    if self.request_date_from_session == 'pm':
                        days -= 0.5
                    if self.request_date_to_session == 'am':
                        days -= 0.5
                    holiday.number_of_days = days
            else:
                holiday.number_of_days = 0
                
    def approve_refuse_timeoff_application(self):
        mail_cc_list = []
        
        timeoff_manager_group_users = self.env['res.users'].search([('groups_id','=',self.env.ref('hr_holidays.group_hr_holidays_manager').sudo().id)])
        hr_employee = self.env['hr.employee'].search([('user_id','in',timeoff_manager_group_users.ids),('department_id.name','=','HR & Admin'),('user_id.company_ids','in',self.employee_id.company_id.id)])
        for mail in hr_employee : mail_cc_list.append(mail.work_email)
        mail_cc = ','.join(mail_cc_list)
        
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menuId = self.env.ref('hr_holidays.menu_open_department_leave_approve').sudo().id
        actionId = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').sudo().id

        approvePageURL = url + '/web#id='+ str(self.id)+ '&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=hr.leave&view_type=list'
        context = {
                    'mail_to':self.employee_id.work_email,
                    'mail_cc':mail_cc,
                    'approvePageURL':approvePageURL
                }
        template_id = self.env['mail.template'].sudo().search([('name','=','Approve/Reject of Timeoff')])
        mail_id = template_id.with_context(context).send_mail(self.id,force_send = True)

    # override method for stop mail from full and final wizard
    def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below
        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env.user.employee_id
        self.filtered(lambda hol: hol.validation_type == 'both').write(
            {'state': 'validate1', 'first_approver_id': current_employee.id})

        # Post a second message, more verbose than the tracking message
        if not self._context.get('from_full_final'):
            for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
                holiday.message_post(
                    body=_(
                        'Your %(leave_type)s planned on %(date)s has been accepted',
                        leave_type=holiday.holiday_status_id.display_name,
                        date=holiday.date_from
                    ),
                    partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()

        if not self._context.get('from_full_final'):
            self.approve_refuse_timeoff_application()
        return True


    def action_refuse(self):
        super(HolidaysRequest, self).action_refuse()
        self.approve_refuse_timeoff_application()


    def _check_employee(self, employee_id):
        if not employee_id:  # to check
            return None
        employee_id = int(employee_id)

        if 'allowed_company_ids' in self.env.context:
            cids = self.env.context['allowed_company_ids']
        else:
            cids = [self.env.company.id]

        Employee = self.env['hr.employee.public'].with_context(allowed_company_ids=cids)
        # check and raise
        if not Employee.check_access_rights('read', raise_exception=False):
            return None
        try:
            Employee.browse(employee_id).check_access_rule('read')
        except AccessError:
            return None
        else:
            return Employee.browse(employee_id)
        
    @api.model
    def create(self,vals):
        _managers_level = 5
        leave_id = super(HolidaysRequest, self).create(vals)

        employee = self._check_employee(leave_id.employee_id.id)
        mail_cc_list = []
        mail_to_list = []
        mail_bcc_list = []
        
        ancestors, current = self.env['hr.employee.public'].sudo(), employee.sudo()
        counter = 0
        while current.parent_id and len(ancestors) < _managers_level+1 and current != current.parent_id:
            ancestors += current.parent_id
            if current.parent_id.parent_id:
                counter += 1
                mail_to_list.append(current.parent_id.work_email) if counter == 1 else mail_bcc_list.append(current.parent_id.work_email)
            elif counter == 0:
                mail_to_list.append(current.parent_id.work_email)
            current = current.parent_id

        mail_to = ','.join(mail_to_list)
        mail_bcc = ','.join(mail_bcc_list)
        
        timeoff_manager_group_users = self.env['res.users'].search([('groups_id','=',self.env.ref('hr_holidays.group_hr_holidays_manager').sudo().id)])
        hr_employee = self.env['hr.employee'].search([('user_id','in',timeoff_manager_group_users.ids),('department_id.name','=','HR & Admin'),('user_id.company_ids','in',leave_id.employee_id.company_id.id)])

        for mail in hr_employee : mail_cc_list.append(mail.work_email)
        mail_cc = ','.join(mail_cc_list)
        
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        menuId = self.env.ref('hr_holidays.menu_open_department_leave_approve').sudo().id
        actionId = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').sudo().id

        approvePageURL = url + '/web#id='+ str(leave_id.id)+ '&menu_id='+str(menuId)+'&action='+str(actionId)+'&model=hr.leave&view_type=list'
        context = {
                    'mail_to':mail_to,
                    'mail_cc':mail_cc,
                    'approvePageURL':approvePageURL
                }
        template_id = self.env['mail.template'].sudo().search([('name','=','Employee Leave Mail')])
        mail_id = template_id.with_context(context,with_bcc=mail_bcc and True or False, with_email_bcc=mail_bcc).send_mail(leave_id.id,force_send = True)
        return leave_id

    # allocate_reasons = fields.Selection(ALLOCATE_REASON, 'Allocate Reason')
    #     sequence = fields.Integer('sequence')
    #     own_leave = fields.Boolean(compute='_compute_own_leave', string="Own leave",
    #                                help="Display Cancel button on own leave")
    #                               states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
    #                               copy=False)
    #     # Get month start and end date
    # forward_to = fields.Many2one('hr.employee', "Forwarded To", readonly=True,
    #                                 domain=[('with_organization', '=', True)])
    #     short_fall = fields.Boolean('Due To Short-fall')
    #     holiday_status_id = fields.Many2one("hr.leave.type", "Leave Type", required=True, readonly=True,
    #                                         states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
    #                                         domain=_domain_leave_type)
    #     color = fields.Integer("Color", related='holiday_status_id.color')
    #     payslip_status = fields.Boolean(string='Reported in last payslips',
    #                 help='Green this button when the leave has been taken into account in the payslip.')
    # def _domain_leave_type(self):
    #     id_list = []
    #     group_hr_manager = self.env['res.users'].has_group('hr.group_hr_manager')
    #     group_hr_officer = self.env['res.users'].has_group('hr.group_hr_user')
    #     employeeObj = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)])
    #     if group_hr_officer or group_hr_manager:
    #         leaveTypeObj = self.env['hr.leave.type'].search([])
    #     else:
    #         if employeeObj and employeeObj.emp_state == 'on_notice' or employeeObj.emp_state == 'training':
    #             leaveTypeObj = self.env['hr.leave.type'].search([('allow_in_notice', '=', True)])
    #         else:
    #             leaveTypeObj = self.env['hr.leave.type'].search([])
    #     for leave_type in leaveTypeObj:
    #         id_list.append(leave_type.id)
    #     return [('id', 'in', id_list)]

    # TODO : Need to Comment or Remove after Leave Script.
    # @api.constrains('holiday_allocation_id')
    # def _check_allocation_id(self):
    #     for leave in self:
    #         if leave.holiday_type == 'employee' and leave.multi_employee and \
    #                 leave.holiday_status_id.requires_allocation == 'yes' and leave.holiday_allocation_id:
    #             raise ValidationError(_(
    #                 'Could not find an allocation of type %(leave_type)s for the requested time period.',
    #                 leave_type=leave.holiday_status_id.display_name,
    #             ))

    # TODO : Need to Comment or Remove after Leave Script.
    # @api.constrains('date_from', 'date_to', 'employee_id')
    # def _check_date_state(self):
    #     if self.env.context.get('leave_skip_state_check'):
    #         return
    #     for holiday in self:
    #         if holiday.state in ['cancel', 'refuse', 'validate1']:
    #             raise ValidationError(_("This modification is not allowed in the current state."))

    # TODO : Need to Comment or Remove after Leave Script.
    # @api.constrains('state', 'number_of_days', 'holiday_status_id')
    # def _check_holidays(self):
    #     for holiday in self:
    #         if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.requires_allocation == 'no':
    #             continue
    #         mapped_days = holiday.holiday_status_id.get_employees_days([holiday.employee_id.id], holiday.date_from)
    #         leave_days = mapped_days[holiday.employee_id.id][holiday.holiday_status_id.id]

    # TODO : Need to Comment or Remove after Leave Script.
    # @api.constrains('date_from', 'date_to', 'employee_id')
    # def _check_date(self):
    #     if self.env.context.get('leave_skip_date_check', False):
    #         return
    #     for holiday in self.filtered('employee_id'):
    #         domain = [
    #             ('date_from', '<', holiday.date_to),
    #             ('date_to', '>', holiday.date_from),
    #             ('employee_id', '=', holiday.employee_id.id),
    #             ('id', '!=', holiday.id),
    #             ('state', 'not in', ['cancel', 'refuse', 'validate']),
    #         ]
    #         nholidays = self.search_count(domain)
    #         if nholidays:
    #             raise ValidationError(
    #                 _('You can not set 2 time off that overlaps on the same day for the same employee.'))

    def write(self,vals):
        today = datetime.now().date()
        if 'request_date_from' in vals:
            date_from_obj = datetime.strptime(vals['request_date_from'],'%Y-%m-%d').date()
            date_to_obj = datetime.strptime(vals['request_date_to'],'%Y-%m-%d').date()
            if (self.env['res.users'].has_group('hr.group_hr_manager')) or (self.request_date_from == date_from_obj and self.request_date_to == date_to_obj):
                pass
            elif date_from_obj <= today  or date_to_obj <= today:
                raise ValidationError("Sorry, you can't Edit leaves for past dates")

        return super(HolidaysRequest, self).write(vals)
    
    
    @api.constrains('holiday_status_id', 'date_from', 'date_to')
    def check_valid(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        current_date = datetime.now().date()
        if self.holiday_status_id.sequence == 4:
            if self.employee_id.confirm_date:
                if self.employee_id.gender != 'female':
                    raise ValidationError(_(Constant.NOT_FEMALE))
                conf_date = str(self.employee_id.confirm_date)
                confirm_date = parser.parse(conf_date)
                difference_in_years = relativedelta(current_date, confirm_date).years
                from_date = datetime.strptime(str(self.date_from), DATETIME_FORMAT)
                to_date = datetime.strptime(str(self.date_to), DATETIME_FORMAT)
                # After 2 month date from form_date
                limit_date = from_date + relativedelta(months=+2)
                holidays_obj = self.env['hr.leave']
                domain = [('employee_id', '=', self.employee_id.id),
                          ('holiday_status_id', '=', self.holiday_status_id.id), ('type', '=', 'remove'),
                          ('state', 'not in', ('cancel', 'refuse'))]
                leave_count = holidays_obj.search_count(domain)
                if difference_in_years < 1:
                    raise ValidationError(_(Constant.NOT_COMPLETE_ONE_YEAR))
                if leave_count > 2:
                    raise ValidationError(_(Constant.NOT_MORE_THAN_TWO_TIMES))
                if to_date > limit_date:
                    raise ValidationError(_(Constant.NOT_MORE_THAN_TWO_MONTH))
            else:
                raise ValidationError(_(Constant.NOT_CONFIRMED_EMPLOYEE))
        domain = [
            ('date_from', '>=', current_date),
            ('date_from', '<=', self.request_date_from),
            ('resource_id' , '=', self.employee_id.resource_id.id),
        ]
        n_holidays = self.env['resource.calendar.leaves'].search(domain)
        working_days = 0
        difference = self.request_date_from - current_date
        for i in range(difference.days + 1):
            data_date = current_date + timedelta(i)
            if self.check_working_day(data_date):
                working_days += 1
        working_days = working_days - len(n_holidays) - 2
        # TODO : Need to uncomment after Leave Script.
        if self.holiday_status_id.sequence in (1, 3, 6):
            if working_days < self.holiday_status_id.no_days:
                if self.env['res.users'].has_group('hr.group_hr_manager') and not self.employee_id.id == self._context.get('uid'):
                    pass
                else:
                    raise ValidationError(
                        _('Sorry, you must apply ' + str(self.holiday_status_id.name) + ' before ' + str(
                            self.holiday_status_id.no_days) + ' working days.'))
        if self.employee_id.state_name == 'Notice':
            if self.holiday_status_id.sequence != 5:
                raise ValidationError(
                    _('Sorry, you are in Notice Period, you can not apply for other leaves except LOP..'))

        difference_unplanned = current_date - self.request_date_from
        for i in range(difference_unplanned.days + 1):
            data_date = current_date - timedelta(i)
            if self.check_working_day(data_date):
                working_days += 1
        working_days = working_days - len(n_holidays)

        # current_month_end_date = current_date + relativedelta(day=31)
        timeoff_month_end_date = self.request_date_from + relativedelta(day=31)
        remaining_total_days = (timeoff_month_end_date - current_date).days

        if self.holiday_status_id.sequence == 2:
            if ((self.request_date_from.month != current_date.month) or (working_days > self.holiday_status_id.no_days)):
                if self.env['res.users'].has_group('hr.group_hr_manager') and not self.employee_id.id == self._context.get('uid'):
                    pass
                elif self.request_date_from.month > current_date.month:
                    pass
                else:    
                    if (remaining_total_days < self.holiday_status_id.no_days and self.request_date_from.month <= current_date.month):
                        raise ValidationError(
                            _('Sorry, ' + str(self.holiday_status_id.name) + ' must be applied before ' + str(timeoff_month_end_date)))
                    else:    
                        raise ValidationError(
                            _('Sorry, ' + str(self.holiday_status_id.name) + ' must be applied within ' + str(
                                self.holiday_status_id.no_days) + ' working days.'))
        return True

    def check_working_day(self, data_date):
        is_working = False
        users_data = self.env['res.users'].browse(self.user_id.id)
        date_code = self.get_day_code(data_date)
        sql = 'SELECT "' + date_code.lower() + '" FROM res_company where id=' + str(users_data.company_id.id)
        self.env.cr.execute(sql)
        rows = self.env.cr.dictfetchall()
        for i in rows[0]:
            if i:
                is_working = True
        return is_working

    def get_day_code(self, data_date):
        first_day = data_date.replace(day=1)
        dom = data_date.day
        remainder = dom % 7
        week_int = dom // 7
        if remainder > 0:
            week_int += 1

        return 'w' + str(week_int) + data_date.strftime("%A")[:3]

    # def create(self, values):
    # super(HolidaysRequest, self).create()
    # if self.employee_id.state_name == 'Notice':
    #     if self.holiday_status_id.sequence != 5:
    #         raise ValidationError(
    # _('Sorry, you are in Notice Period, you can not apply for other leaves except LOP..'))
    # return super(HolidaysRequest, self).create(values)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    remaining_leaves = fields.Float(string='Planned Leaves', compute='_get_remaining_days',
                                    help='Total Planned Leaves', readonly=True)  # compute='_get_remaining_days',
    remaining_unplanned_leaves = fields.Float(string='Unplanned Leaves', compute='_get_unplanned_days',
                                              help='Total Unplanned Leaves',
                                              readonly=True)  # compute='_get_unplanned_days',
    remaining_floating_leaves = fields.Float(string='Floating Leaves', compute='_get_floating_days',
                                             help='Total Floating Leaves',
                                             readonly=True)  # compute='_get_floating_days',
    leaves_count = fields.Float(string='Leaves')  # compute='_leaves_count',

    leave_in_notice = fields.Char(compute='_get_leave_in_notice', string='Leave in notice period')
    # def create(self, vals):
    #     # don't pass the value of remaining leave if it's 0 at the creation time, otherwise it will trigger the inverse
    #     # function _set_remaining_days and the system may not be configured for. Note that we don't have this problem on
    #     # the write because the clients only send the fields that have been modified.
    #     if 'remaining_leaves' in vals and not vals['remaining_leaves']:
    #         del (vals['remaining_leaves'])
    #     return super(HrEmployee, self).create(vals)

    def _get_remaining_days(self):
        emp_obj = self.env['hr.leave.allocation'].search([('employee_id', '=', self.id),
                                                          ('holiday_status_id.sequence', '=', 1)])
        self.remaining_leaves = emp_obj.holiday_status_id.remaining_leaves

    def _get_unplanned_days(self):
        emp_obj = self.env['hr.leave.allocation'].search([('employee_id', '=', self.id),
                                                          ('holiday_status_id.sequence', '=', 2)])
        self.remaining_unplanned_leaves = emp_obj.holiday_status_id.remaining_leaves

    def _get_floating_days(self):
        emp_obj = self.env['hr.leave.allocation'].search([('employee_id', '=', self.id),
                                                          ('holiday_status_id.sequence', '=', 3)])
        self.remaining_floating_leaves = emp_obj.holiday_status_id.remaining_leaves

    def _leaves_count(self):
        res = {}
        leaves = self.env['hr.leave.allocation'].read_group([
            ('employee_id', 'in', self.ids),
            ('holiday_status_id.limit', '=', False), ('state', '=', 'validate')],
            fields=['number_of_days', 'employee_id'], groupby=['employee_id'])
        res.update(dict([(leave['employee_id'][0], leave['number_of_days']) for leave in leaves]))
        for leaves in res.values():
            self.leaves_count = leaves

    def _get_leave_in_notice(self):
        no_of_days = 0.0
        for rec in self:
            hr_holidays_obj = self.env['hr.leave'].search([
                ('employee_id', '=', rec.id),
                ('date_from', '>=', rec.resignation_date),
                ('type', '=', 'remove'),
            ])  # ('type', '=', 'remove'),
            for hr_holiday in hr_holidays_obj:
                no_of_days = no_of_days + (hr_holiday.number_of_days * -1)
            rec.leave_in_notice = str(no_of_days) + ' days'        

# '''  Need to this discuss with RK
# class resource_calendar_leaves(models.Model):
#     _inherit = "resource.calendar.leaves"
#     _name = "resource.calendar.leaves"
#
#
# # # Calculate plannned/unplanned leave for old policy
# # def calculate_leaves(total_leave):
# #     result = {'value': {}}
# #     leaves = int(total_leave / 4)
# #     remindar = int(total_leave % 4)
# #     planned_leave = leaves * 3 + remindar
# #     unplanned_leave = leaves
# #     result['value']['planned_leave'] = planned_leave
# #     result['value']['unplanned_leave'] = unplanned_leave
# #     return result
# '''
#
# # New Calculate planned/unplanned leave for old policy
# def calculate_leaves(total_leave):
#     result = {'value': {}}
#     planned_leave = total_leave * (
#             Constant.PLANNED_LEAVE_RATIO1 / float(Constant.PLANNED_LEAVE_RATIO1 + Constant.PLANNED_LEAVE_RATIO2))
#     rounded_planned_leave = 0.5 * math.ceil(planned_leave / 0.5)
#     unplanned_leave = total_leave - rounded_planned_leave
#     result['value']['planned_leave'] = rounded_planned_leave
#     result['value']['unplanned_leave'] = unplanned_leave
#     return result
#

# # Calculate leave as per new leave policy
def calculate_leaves_new(planned_leave, total_leave):
    result = {'value': {}}
    planned_leave = (24 * planned_leave) / total_leave
    planned_leave = round(planned_leave)
    unplanned_leave = 24 - planned_leave
    result['value']['planned_leave'] = planned_leave
    result['value']['unplanned_leave'] = unplanned_leave
    return result
