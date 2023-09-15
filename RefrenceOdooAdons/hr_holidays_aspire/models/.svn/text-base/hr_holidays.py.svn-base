# Inherit hr.holiday module
import logging
from datetime import date, timedelta
import datetime
import math
import datetime
import time
from math import ceil
import calendar
from operator import attrgetter
from openerp.exceptions import Warning
from openerp import tools, models, fields, api
from openerp.osv import fields, osv
from openerp.tools.translate import _
from dateutil.relativedelta import relativedelta
from dateutil import parser
from openerp import models
from ..constant.constant import Constant
from openerp.exceptions import ValidationError, except_orm

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
 
_logger = logging.getLogger(__name__)

ALLOCATE_REASON = [
    ('compensation', 'Compensation'),
]

INTERVAl = [
    ('monthly', 'Monthly'),
    ('yearly', 'Yearly'),
]


class hr_holidays_status(osv.osv):
    _inherit = 'hr.holidays.status'
    _description = "Leave Type"

    # Overide get days function
    def get_days(self, cr, uid, ids, employee_id, context=None):
        result = dict((id, dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
                                virtual_remaining_leaves=0)) for id in ids)
        domain = [('employee_id', '=', employee_id),('state', 'in', ['confirm', 'validate1', 'validate']),('holiday_status_id', 'in', ids)]
        holiday_ids = self.pool['hr.holidays'].search(cr, uid, domain, context=context)
        # print "==holiday_ids==",holiday_ids
        for holiday in self.pool['hr.holidays'].browse(cr, uid, holiday_ids, context=context):
            status_dict = result[holiday.holiday_status_id.id]
            if holiday.type == 'add' or holiday.type == 'carry_forward':
                status_dict['virtual_remaining_leaves'] += holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['max_leaves'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] += holiday.number_of_days_temp
            elif holiday.type == 'remove' or holiday.type == 'lapsed':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= holiday.number_of_days_temp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= holiday.number_of_days_temp
        return result

    _columns = {
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of state."),   
        'no_leave': fields.integer('No Of Leaves', help="No Of Leaves To Add"), 
        'add_interval' :fields.selection(INTERVAl,'Interval'),
        'no_days' :fields.integer('No of Days'), 
        'allow_in_notice' :fields.boolean('Allow in notice period'),    
    }

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not context.get('employee_id',False):
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee
            return super(hr_holidays_status, self).name_get(cr, uid, ids, context=context)
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if not record.limit:
                name = name + ('  (%g)' % (record.remaining_leaves or 0.0))
            res.append((record.id, name))
        return res

# Inherit hr.holidays model
class hr_holidays(osv.osv):
   
    _name = 'hr.holidays'
    _inherit = ['hr.holidays', 'mail.thread', 'ir.needaction_mixin']
    _order = "type desc, date_from asc"
  
    def _compute_number_of_days(self, cr, uid, ids, name, args, context=None):
        result = {}
        for hol in self.browse(cr, uid, ids, context=context):
            if hol.type =='remove' or hol.type == 'lapsed':
                result[hol.id] = -hol.number_of_days_temp
            else:
                result[hol.id] = hol.number_of_days_temp
        return result

    # Check apply leave is own or not
    def  _compute_own_leave(self, cr, uid, ids, name, args, context=None):
        res = {}
        for record in self.browse(cr,uid,ids,context):
            if uid == record.employee_id.user_id.id:
                res[record.id] = True
        return res    

    # Override method of existing constraints
    def check_holidays(self, cr, uid, ids, context=None):
        return True

    # Override method
    def _check_date(self, cr, uid, ids, context=None):
        return True

    # Get month start date
    def _compute_month_start(self, cr, uid, ids, name, args, context=None):
        dates = datetime.datetime.now().date()
        month = dates.month
        year = dates.year
        if month == 1:
            month = 12
            year = year-1
        else:
            month = month-1
            year = year
        prev_month_start_date = datetime.date(year, month, 1)
        res = {}
        for record in self.browse(cr,uid,ids,context):
            res[record.id] = prev_month_start_date.strftime("%Y-%m-%d") 
        return res  

    # Get month end date
    def _compute_month_end(self, cr, uid, ids, name, args, context=None):
        dates = datetime.datetime.now().date()
        month = dates.month
        year = dates.year
        start_date = datetime.date(year, month, 1)
        # if month == 12:
        #     month = 1
        #     year = year+1
        # else:
        #     month = month+1
        #     year = year
        prev_month_end_date = start_date - datetime.timedelta (days = 1)
        res = {}
        for record in self.browse(cr,uid,ids,context):
            res[record.id] = prev_month_end_date.strftime("%Y-%m-%d") 
        return res  

    def check_working_day(self,cr, uid, ids,dataDate,context):
        isWorking = False
        usersObj = self.pool['res.users']
        companyObj = self.pool['res.company']
        usersData = usersObj.browse(cr, uid, [uid],context)
        dateCode =  self.getDayCode(cr, uid, ids,dataDate,context)
        sql = 'SELECT "' + dateCode + '" FROM public.res_company where id = ' + str(usersData.company_id.id);
        cr.execute(sql)
        rows = cr.fetchall()
        for i in rows[0]:
            if i:
                isWorking = True
        return isWorking

    def getDayCode(self,cr, uid, ids,dataDate,context):
        first_day = dataDate.replace(day=1)
        dom = dataDate.day
        remainder = dom % 7
        weekInt = dom/7
        if remainder > 0:
            weekInt = weekInt + 1
        print 'W' + str(weekInt) + dataDate.strftime("%A")[:3]
        return 'W' + str(weekInt) + dataDate.strftime("%A")[:3]

    # Check allow to user apply for leave or not
    @api.constrains('holiday_status_id','date_from','date_to','state','number_of_days_temp')
    def _check_holiday_status(self, cr, uid, ids, context=None):
        # print "=== _check_holiday_status ===="
        leave_ids = []
        change_sequence = 0
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        current_date = datetime.datetime.now()
        for record in self.browse(cr, uid, ids, context=context):
            if 'carry_leave' in record:
                if record.carry_leave == True:
                    continue

            # Check maternity leave criteria
            sequence = record.holiday_status_id.sequence
            if sequence == 4 and record.type == 'remove':
                if record.employee_id.confirm_date:
                    if record.employee_id.gender != 'female':
                        raise ValidationError(_(Constant.MATERNITY_NOT_FEMALE))    
                  
                    confirm_date =   parser.parse(record.employee_id.confirm_date)
                    difference_in_years = relativedelta(current_date,confirm_date).years
                    from_date = datetime.datetime.strptime(record.date_from, DATETIME_FORMAT)
                    to_date = datetime.datetime.strptime(record.date_to, DATETIME_FORMAT)
                    # After 2 month date from form_date  
                    limit_date = from_date + relativedelta(months=+2)
                    holidays_obj = self.pool.get('hr.holidays')
                    domain = [('employee_id', '=', record.employee_id.id), ('holiday_status_id','=',record.holiday_status_id.id),('type','=','remove'),('state','not in',('cancel','refuse'))] 
                    leave_count = holidays_obj.search_count(cr, uid, domain, context=context)
                    if difference_in_years < 1:
                        raise ValidationError(_(Constant.NOT_COMPLETE_ONE_YEAR))
                    if leave_count > 2:
                        raise ValidationError(_(Constant.NOT_MORE_THAN_TWO_TIMES))    
                    if to_date > limit_date:
                        raise ValidationError(_(Constant.NOT_MORE_THAN_TWO_MONTH))    
                else:
                    raise ValidationError(_(Constant.NOT_CONFIRMED_EMPLOYEE))            

            # Not check any criteria for leave type is not remove
            if record.holiday_type != 'employee' or record.type != 'remove' or not record.employee_id or record.holiday_status_id.limit:
                continue      
            
            # Avaliable leave is not enough
            leave_days = self.pool.get('hr.holidays.status').get_days(cr, uid, [record.holiday_status_id.id], record.employee_id.id, context=context)[record.holiday_status_id.id]
            # print leave_days
            if leave_days['remaining_leaves'] < 0 or leave_days['virtual_remaining_leaves'] < 0:
                # Raising a warning gives a more user-friendly feedback than the default constraint error
                raise ValidationError(_(Constant.LEAVE_NOT_AVAILABLE))
            
            from_date = datetime.datetime.strptime(record.date_from, DATETIME_FORMAT)
            to_date = datetime.datetime.strptime(record.date_to, DATETIME_FORMAT)
            timedelta = from_date - current_date  
            day = timedelta.days + 1

            if not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_user') and not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_reporting_authority'):
                # Check planned leave criteria
                holiday_leave_object = self.pool.get('hr.holidays.detail')
                domain = [
                    ('holiday_from', '>=', current_date),
                    ('holiday_from', '<=', from_date),
                ]

                nholidays = holiday_leave_object.search(cr, uid, domain, context=context)
                start_date =  datetime.datetime.now().date()
                end_date = datetime.datetime.strptime(from_date.strftime('%Y-%m-%d'), '%Y-%m-%d').date()
                working_days = 0
                diff = end_date - start_date
                attenRecSumObj = self.pool.get('attendance.daily_summary')
                for i in range(diff.days + 1):
                    dataDate =  start_date + datetime.timedelta(i)
                    if self.check_working_day(cr,uid,ids,dataDate,context):
                        # print dataDate
                        working_days+=1
                working_days = working_days - len(nholidays) - 2

                if working_days < record.holiday_status_id.no_days:
                    raise ValidationError(_('Sorry, you must apply '+ str(record.holiday_status_id.name) +' before ' + str(record.holiday_status_id.no_days) + ' working days.'))
                # if str(record.holiday_status_id.name) in 'Planned leave':                    
                #     if working_days < 2 : 
                      
                #         raise ValidationError(_(Constant.INVALID_PLANNED_LEAVE))

                # if str(record.holiday_status_id.name) in 'Compensation Leave':                    
                #     if working_days < 2 : 
                #         raise ValidationError(_(Constant.INVALID_PLANNED_LEAVE))
               
                # # Check unplanned leave creiteria 
                # if str(record.holiday_status_id.name) in 'Unplanned Leaves':
                #     # In Unplanned leave apply before current date
                #     if record.adjust_plannedleave == True:
                #         return True
                    # if (record.date_from and record.date_to) and (from_date > current_date ) and (to_date > current_date):
                    #     raise ValidationError(_(Constant.INVALID_UNPLANNED_LEAVE))


                # # Check floating holidays criteria
                # if str(record.holiday_status_id.name) in 'Floating Holidayzzz':
                #     if day < 7:
                #         raise ValidationError(_(Constant.INVALID_FLOATING_LEAVE))             
        return True

    # Check enter no of days is valid or not as per calculation
    @api.constrains('number_of_days_temp')
    def _check_no_of_days_valid(self, cr, uid, ids, context=None): 
        for data in self.browse(cr, uid, ids , context = context):
            if 'carry_leave' in data:
                if data.carry_leave == True:
                    return True
            
            # Check type is add only check no of days must be greater than zero
            if 'type' in data:
                if data.type == 'add':
                    if data.number_of_days_temp <= 0 :
                        raise ValidationError(_(Constant.INVALID_NO_OF_DAYS))             
                    else:
                        return True

            # Check this value if type is 'remove'
            no_of_days = self.onchange_date_from(cr, uid, ids, data.date_from, data.date_to, data.from_session, data.to_session, data.employee_id)
            no_of_days = no_of_days['value']['number_of_days_temp']
            if no_of_days <= 0:
                raise ValidationError(_(Constant.INVALID_NO_OF_DAYS))             

            if no_of_days !=  data.number_of_days_temp:
                raise ValidationError(_(Constant.INVALID_NO_OF_DAYS))             
        return True

    # Constraints for check overlap applay leaves or not
    @api.constrains('date_from','date_to','from_session','to_session')
    def _check_date_new(self, cr, uid, ids, context=None):
        for holiday in self.browse(cr, uid, ids, context=context):
            if (holiday.date_from and holiday.date_to) == False:
                return True
            date_from = parser.parse(holiday.date_from)
            date_to = parser.parse(holiday.date_to)
            date_from = date_from.strftime("%Y-%m-%d")
            date_to = date_to.strftime("%Y-%m-%d") 
            domain = [
                ('date_from', '<=', date_to ),
                ('date_to', '>=', date_from ),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search(cr, uid, domain, context=context)
            for record in self.browse(cr, uid, nholidays, context=context):
                old_from_session = record.from_session
                old_to_session = record.to_session
                old_from_date = parser.parse(record.date_from)
                old_to_date = parser.parse(record.date_to)
                new_from_session = holiday.from_session
                new_to_session = holiday.to_session

                if old_from_session == 'session1' and old_to_session == 'session2':
                    raise ValidationError(_(Constant.NOT_OVERLAP_LEAVE))                    

                if old_from_date.strftime("%Y-%m-%d") == date_from and old_to_date.strftime("%Y-%m-%d") == date_to:
                    if old_from_session == new_from_session or old_to_session == new_to_session:
                        raise ValidationError(_(Constant.NOT_OVERLAP_LEAVE))                    
                    else:
                        continue
                
                if date_from <= old_from_date.strftime("%Y-%m-%d")  and date_to == old_from_date.strftime("%Y-%m-%d") :
                    if old_from_session == 'session1' or new_to_session == 'session2':
                        raise ValidationError(_(Constant.NOT_OVERLAP_LEAVE))                    

                if date_from == old_to_date.strftime("%Y-%m-%d") and  date_to >= old_to_date.strftime("%Y-%m-%d") :
                    if old_to_session == 'session2' or new_from_session == 'session1':
                        raise ValidationError(_(Constant.NOT_OVERLAP_LEAVE))                    

                if date_from < old_from_date.strftime("%Y-%m-%d") and date_to > old_to_date.strftime("%Y-%m-%d") :
                    raise ValidationError(_(Constant.NOT_OVERLAP_LEAVE))                    
        return True

    # Check select session is valid or not
    @api.constrains('from_session','to_session')
    def _check_session(self, cr, uid, ids, context=None):
        for holiday in self.browse(cr, uid, ids, context=context):
            if (holiday.date_from and holiday.date_to) != False:
                date_from = parser.parse(holiday.date_from)
                date_to = parser.parse(holiday.date_to)
                if date_from.strftime("%Y-%m-%d") ==  date_to.strftime("%Y-%m-%d"):
                    if holiday.from_session == 'session2' and holiday.to_session == 'session1':
                        raise ValidationError(_(Constant.INVALID_SESSION))                    
        return True 

    def _domain_leave_type(self):        
        id_list = []
        group_hr_manager = self.env['res.users'].has_group('base.group_hr_manager')
        group_hr_officer = self.env['res.users'].has_group('base.group_hr_user')
        employeeObj = self.env['hr.employee'].search([('user_id','=',self.env.user.id)])
        if group_hr_officer or group_hr_manager:
            leaveTypeObj =  self.env['hr.holidays.status'].search([])
        else:
            if employeeObj and employeeObj.emp_state == 'on_notice':
                leaveTypeObj =  self.env['hr.holidays.status'].search([('allow_in_notice','=',True)])
            else:
                leaveTypeObj =  self.env['hr.holidays.status'].search([])
        for leave_type in leaveTypeObj:
            id_list.append(leave_type.id)
        return [('id', 'in', id_list)]
        

    _columns = {
        'name': fields.char('Description',required=True),
        'state': fields.selection([('draft', 'To Submit'), ('cancel', 'Cancelled'),('confirm', 'To Approve'), ('refuse', 'Refused'), ('validate1', 'Second Approval'), ('validate', 'Approved')],
            'Status', readonly=True, track_visibility='onchange', copy=False,
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.'),
        'from_session': fields.selection([('session1', 'Session 1'), 
            ('session2', 'Session2')],
            'From Session', select=True, readonly=True, 
            states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]} ),
        'to_session': fields.selection([('session1', 'Session 1'), 
            ('session2', 'Session2')],
        'To Session', select=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]} ),
        'adjust_plannedleave':fields.boolean('Adjust planned leave with unplanned leave'),
        'document':fields.binary('Document'),
        'carry_leave':fields.boolean('Carry forward leave', default=False),
        'type': fields.selection([('remove','Removed'),('add','Added'),('lapsed','Lapsed Leave'),('carry_forward','Carry Forward')], 'Request Type', required=True, readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, help="Choose 'Leave Request' if someone wants to take an off-day. \nChoose 'Allocation Request' if you want to increase the number of leaves available for someone", select=True),
        'number_of_days': fields.function(_compute_number_of_days, string='Number of Days', store=True,),
        'granted_date': fields.datetime('Date', states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}),
        'allocate_reasons':fields.selection(ALLOCATE_REASON,'Allocate Reason'),
        'sequence' : fields.integer('sequence'),
        'own_leave':fields.function(_compute_own_leave,type='boolean',string="Own leave", help="Display Cancel button on own leave"),
        'date_to': fields.datetime('End Date', readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]}, copy=False),
        # Get month start and end date
        'month_start': fields.function(_compute_month_start, string='Month Start', type='datetime'),
        'month_end': fields.function(_compute_month_end, string='Month End', type='datetime'),
        'forward_to':fields.many2one('hr.employee',"Forwarded To",readonly=True,domain=[('with_organization','=',True)]),
        'short_fall': fields.boolean('Due To Short-fall'),
        'holiday_status_id': fields.many2one("hr.holidays.status", "Leave Type", required=True,readonly=True, states={'draft':[('readonly',False)], 'confirm':[('readonly',False)]},domain=_domain_leave_type),
        
    }

    _defaults = {
        'state':'draft',
        'granted_date':  datetime.datetime.now(),
        
    }

    _constraints = [
        #(_check_holiday_status, 'The number of remaining leaves is not sufficient for this leave type', ['holiday_status_id','date_from','date_to','state','number_of_days_temp']),
        (_check_date, 'You can not have 2 leaves that overlaps on same', ['date_from','date_to']), # Overide Constraints of existing module
        #(_check_date_new, Constant.NOT_OVERLAP_LEAVE, ['date_from','date_to','from_session','to_session']),
        #(_check_session, Constant.INVALID_SESSION, ['from_session','to_session']),
        #(_check_no_of_days_valid, Constant.INVALID_NO_OF_DAYS, ['number_of_days_temp']),
    ] 

    # Overide sql_constriants method
    def _auto_init(self, cr, context=None):
        self._sql_constraints = [
        ('date_check', "CHECK (1=1)", "The number of days must be greater than 0."),
        ]
        super(hr_holidays, self)._auto_init(cr, context)

    
    # Add leaves schedular
    def leave_schedular(self, cr, uid, context=None):
        # print "Carry forwarded leave after year 2016 and month is first"
        # Carry forwarded leave after year 2016 and month is first
        
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        try:
            if current_month == 1 and current_year > 2016:
                # print "=========== leaves_forward_new_policy ========"
                leave_forwarded = self.leaves_forward_new_policy(cr, uid, context=None)
                # print leave_forwarded
        except Exception, e:
            _logger.error('Something is wrong')
            _logger.error(str(e))
        # Add employee leave as per monthly and yearly in leave types
        try:
            leave_type_object = self.pool.get('hr.holidays.status')
            leave_type_ids = leave_type_object.search(cr, uid, [('active', '=', 'True')])
            for record in leave_type_object.browse(cr, uid, leave_type_ids, context):
                if record.add_interval and record.no_leave:
                    if record.add_interval == 'yearly':
                        if current_month != 1:
                            continue
                    # print "============== add leave tpye and No. ==========="
                    add_leave = self.add_leave(cr, uid, record)
                    
                else:
                    continue
        except Exception, e:
           _logger.error('Something is wrong')
           _logger.error(str(e))
        
        return True

    # Add leave function for all leave type
    def add_leave(self, cr, uid, record, context=None):
        try:   
            current_year = datetime.datetime.now().year
            employee_obj = self.pool.get('hr.employee')
            leave_type_obj = self.pool.get('hr.holidays.status')
            holidays_obj = self.pool.get('hr.holidays')
           
            # Calculate Month start and end date
            dates = datetime.datetime.now()
            month = dates.month
            year = dates.year
            month_start = datetime.date(year, month, 1).strftime("%Y-%m-%d")
            if month == 12:
                month = 1
                year = year+1
            else:
                month = month+1
                year = year
            month_end = (datetime.date (year, month, 1) - datetime.timedelta (days = 1)).strftime("%Y-%m-%d")
        
            # If record then add leaves 
            if record:
                add_leave = record.no_leave # Add leave no in leave types
                emp_ids = employee_obj.search(cr, uid, [('with_organization', '=',True)])
                leave_ids = []
                for emp in employee_obj.browse(cr, uid, emp_ids):
                    add_leave = record.no_leave
                    # print "=========+++++ add leave +++++++++>>>>"
                    # print add_leave
                    if emp.emp_state == 'on_notice':
                        continue
                    if emp.emp_state == 'training':
                        continue
                    if emp.emp_state == 'new':
                        continue
                    if emp.emp_state == 'probation' and record.name in ["Unplanned Leaves","Floating Holiday","Maternity Leaves"]:
                        continue
                    if emp.with_organization == False:
                        continue
                    # If cureent year is 2015 and add leave is planned leave
                    if current_year == 2015 and record.sequence == "Planned Leaves":
                        if emp.emp_state == 'confirmed':
                            add_leave = 2                    

                    
                    # Check current month leave is added or not 
                    domain = [('employee_id','=', emp.id,),('type','=','add'),('granted_date','>=',month_start),('granted_date','<=',month_end),('holiday_status_id','=',record.id)]
                    is_added = holidays_obj.search(cr,uid,domain)
                        # Continue if leave is added for current month
                    if is_added:
                        # print " ====== is_added ========",is_added
                        continue
                    # End check process of employee leave is add or not
                    vals = {
                        'name': _('Leave Granted to %s') % emp.name,
                        'state':'confirm',
                        'employee_id': emp.id,
                        'holiday_status_id': record.id,
                        'type': 'add',
                        'holiday_type':'employee',
                        'number_of_days_temp': add_leave,
                        'adjust_plannedleave':False
                    }
                    # print "Added value",vals
                    leave_ids.append(holidays_obj.create(cr, uid, vals, context=None))
                    # Approve leave request
                for leave_id in leave_ids:
                    for sig in ('confirm', 'validate', 'second_validate'):
                        self.signal_workflow(cr, uid, [leave_id], sig)

                # Send Mail to hr when run schedular
                '''try:
                    template = self.pool.get('ir.model.data').get_object(cr, uid, 'hr_holidays_aspire', 'run_schedular')
                    # print "template id",template
                    mail_id = self.pool.get('mail.template').send_mail(cr, uid, template.id, record.id , force_send=True)
                    # print "send mail"
                except Exception, e:
                    _logger.error('Email not send')
                    _logger.error(str(e))'''
                # End send mail schedular

        except Exception, e:
            _logger.error('Something is wrong')
            _logger.error(str(e))
        return True

    # Leave forward as per new policy
    def leaves_forward_new_policy(self, cr, uid, context=None):
        # print "New leave policy is applied"
        employee_obj = self.pool.get('hr.employee')        
        emp_ids = employee_obj.search(cr, uid, [('employee_no', '=like','AS%' )])
        try:
            for emp in employee_obj.browse(cr, uid, emp_ids):
                values = {}
                planned_leaves = emp.remaining_leaves
                unplanned_leave = emp.remaining_unplanned_leaves
                lapsed_floating = emp.remaining_floating_leaves
                if lapsed_floating:
                    remove_lapsed_floating = self.add_remove_employee_leaves(cr, uid, emp.id, 3, lapsed_floating, 'lapsed', context)
                
                total_leave = planned_leaves + unplanned_leave
                if total_leave <= 0:
                    continue
                if total_leave <= 24:
                    continue
                else:
                    values = calculate_leaves_new(planned_leaves,total_leave)
                new_planned = values['value']['planned_leave']
                new_unplanned = values['value']['unplanned_leave']
                lapsed_planned = planned_leaves - new_planned
                lapsed_unplanned = unplanned_leave - new_unplanned
                if lapsed_planned != 0:
                    remove_lapsed_planned = self.add_remove_employee_leaves(cr, uid, emp.id, 1, lapsed_planned, 'lapsed', context)
                if lapsed_unplanned != 0:
                    remove_lapsed_unplanned = self.add_remove_employee_leaves(cr, uid, emp.id, 2, lapsed_unplanned, 'lapsed', context)
        except Exception, e:
            _logger.error('Something is wrong')
            _logger.error(str(e))
        return True

    # Leave carry forwarded for old policy
    def leaves_forward_old_policy(self, cr, uid, context=None):
        current_month = datetime.datetime.now().month
        current_year = datetime.datetime.now().year
        employee_obj = self.pool.get('hr.employee')
        
        if current_month != 1 and current_year != '2016':
            return True

        emp_ids = employee_obj.search(cr, uid, [('employee_no', '=like','AS%' )])
        try:
            for emp in employee_obj.browse(cr, uid, emp_ids):
                values = {}
                lapsed_leave = 0
                remaining_leave = 0
                total_leave = emp.remaining_leaves
                
                # Calculate planned/unplanned leave carry forward 
                if total_leave <= 0:
                    continue
                if total_leave < 30:
                    values = calculate_leaves(total_leave)
                else:
                    carry_leave = 30
                    values = calculate_leaves(carry_leave)

                # Calculate lapsed and remaing carry leaves
                if total_leave > 30:
                    lapsed_leave = total_leave - 30
                    remaining_leave = total_leave - lapsed_leave
               
                if lapsed_leave == 0:
                    remove_total = self.add_remove_employee_leaves(cr, uid, emp.id, 1, total_leave*-1, 'carry_forward' , context)
                else:
                    remove_lapsed = self.add_remove_employee_leaves(cr, uid, emp.id, 1, lapsed_leave, 'lapsed', context)
                    remove_remaining = self.add_remove_employee_leaves(cr, uid, emp.id, 1, remaining_leave*-1, 'carry_forward', context)                

                planned_leave = self.add_remove_employee_leaves(cr, uid, emp.id, 1, values['value']['planned_leave'], 'carry_forward', context)
                unplanned_leave = self.add_remove_employee_leaves(cr, uid, emp.id, 2, values['value']['unplanned_leave'], 'carry_forward', context)                
        except Exception, e:
            _logger.error('Something is wrong')
            _logger.error(str(e))
        return True
    

     # Add/Remove leave function for carry forwarded leave
    def add_remove_employee_leaves(self, cr, uid, ids, leave_sequence, no_of_leave, types, context=None):
        # print "=========== add_remove_employee_leaves =========="
        leave_type_obj = self.pool.get('hr.holidays.status')
        holidays_obj = self.pool.get('hr.holidays')
            
        # Holiday leave id
        leave_type_id = leave_type_obj.search(cr, uid, [('sequence', '=', leave_sequence)], context=context)
        if not leave_type_id:
            return False

        # Name message from leave type
        if types == 'carry_forward':
            des = 'Carry forward leave from total'
        else:
            des = 'Lapsed leave from total leave'

        leave_type_id = leave_type_id and leave_type_id[0] or False
        leave_ids = [] # For add leaves
        vals = {
            'name': des,
            'type': types,
            'state':'confirm',
            'holiday_type':'employee',
            'employee_id': ids,
            'holiday_status_id': leave_type_id,              
            'number_of_days_temp': no_of_leave,
            'adjust_plannedleave': False,
            'carry_leave': True,
        }
        leave_ids.append(holidays_obj.create(cr, uid, vals, context=None))
        for leave_id in leave_ids:
            for sig in ('confirm', 'validate', 'second_validate'):
                self.signal_workflow(cr, uid, [leave_id], sig)
        return True

    # Approve leave notification schedular
    def approve_leave_notification_schedular(self, cr, uid, context=None): 
        holiday_obj = self.pool.get('hr.holidays')
        domain = [('state','in',['confirm']),('type','=','remove'),('carry_leave','=',False)]
        holiday_ids = holiday_obj.search(cr, uid, domain, context=context)
        # Send mail to Parent for approve leave
        try:
            for record in holiday_obj.browse(cr, uid, holiday_ids, context=context):
                template = self.pool.get('ir.model.data').get_object(cr, uid, 'hr_holidays_aspire', 'leave_notify')
                mail_id = self.pool.get('mail.template').send_mail(cr, uid, template.id, record.id , force_send=True)
        except Exception, e:
            _logger.error('Email not send')
            _logger.error(str(e))
        return True

    # Count number of days in apply leave
    def _get_number_of_days(self,cr,uid,ids,date_from, date_to,context):
        """Returns a float equals to the timedelta between two dates given as string."""

        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        TOTAL_DAY = 0
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt.date() - from_dt.date()
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        diff_day = round(math.floor(diff_day))+1
        for i in xrange(int(diff_day)):
            DATE = from_dt + datetime.timedelta(days=i)
            dataDate =  DATE.date()
            if self.check_working_day(cr,uid,ids,dataDate,context):
                TOTAL_DAY = TOTAL_DAY + 1
        return TOTAL_DAY

    # # Check apply leave saturaday is even or not
    # def check_other_days(self, dates):
    #     day_no = 0
    #     month = dates.month
    #     year = dates.year
    #     start_date = datetime.date(year, month, 1)
    #     #last_day = calendar.monthrange(year,month)
    #     if month == 12:
    #         month = 1
    #         year = year+1
    #     else:
    #         month = month+1
    #         year = year
        
    #     last_date = datetime.date (year, month, 1) - datetime.timedelta (days = 1)
    #     timedelta = last_date - start_date
    #     for i in xrange(timedelta.days + 1):
    #         DATE = start_date + datetime.timedelta(days=i)
    #         if DATE.weekday() == 5:
    #             day_no = day_no + 1
    #             if DATE.strftime("%Y-%m-%d")  == dates.strftime("%Y-%m-%d") :
    #                 if day_no != 1:
    #                     return True
    #                 else:
    #                     return False

    # Count holiday leave in apply leave 
    def count_holiday_leave(self, cr, uid, from_date, to_date):
        holiday_leave_object = self.pool.get('hr.holidays.detail')
        domain = [
            ('holiday_from', '<=', to_date),
            ('holiday_from', '>=', from_date),
        ]
        nholidays = holiday_leave_object.search_count(cr, uid, domain, context=None)
        return nholidays

    def _check_start_end_holiday(self, cr, uid, date_from):
        ids = []
        diff_day = self._get_number_of_days(cr,uid,ids,date_from, date_from,context=None)
        holiday_leave = self.count_holiday_leave(cr, uid, date_from, date_from)
        TOTAL_DAY = diff_day - holiday_leave
        return TOTAL_DAY


    # On Change dates and session option count no of datys
    def onchange_date_from(self, cr, uid, ids, date_from, date_to, from_session, to_session,employee_id):
       
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        value = 0
        total_leave = 0
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_( Constant.INVALID_SESSION))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_to_with_delta = datetime.datetime.strptime(date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            result['value']['date_to'] = str(date_to_with_delta)

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            ids = []
            diff_day = self._get_number_of_days(cr,uid,ids,date_from, date_to,context=None)
            holiday_leave = self.count_holiday_leave(cr, uid, date_from, date_to) # Calculate holidays leave in apply leave by employee
            total_day = diff_day - holiday_leave
            total_leave = total_day
            if not from_session or not to_session :
                total_leave = total_day
            
            if (from_session and to_session) and from_session == 'session1' and to_session == 'session2':  
                total_leave = total_day
            
            check_start_date_holiday = self._check_start_end_holiday(cr, uid, str(date_from))
            if check_start_date_holiday != 0 and from_session == 'session2':
                total_leave = total_leave - 0.5

            ckeck_end_date_holiday = self._check_start_end_holiday(cr, uid ,str(date_to))
            if ckeck_end_date_holiday != 0 and to_session == 'session1':
                total_leave = total_leave - 0.5

            if total_day < 0:
                    total_leave = 0 

            result['value']['number_of_days_temp'] = total_leave
        return result

    def onchange_holiday_status_id(self, cr, uid, ids, holiday_status_id, context= None): 
        result = {'value': {}}
        if holiday_status_id:
            holiday_sequence = self.pool.get('hr.holidays.status').browse(cr, uid, holiday_status_id, context = context)
            result['value']['sequence'] = holiday_sequence.sequence
        return result
   
    # Override parent method
    # Create Remove/Add Leave request
    def create(self, cr, uid, values, context=None):
        sequence = 0
        res = False
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog = True)
        
        # Manager and Reporting authority can only approve and reject leave
        if values.get('state') and values['state'] not in ['draft', 'confirm', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_user'):
            raise osv.except_osv(_('Warning!'), _('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % values.get('state'))
       
        holiday_id = values['holiday_status_id']
        planned_id = self.pool.get('hr.holidays.status').search(cr, uid, [('id', '=', holiday_id)], context=context)
        for record in self.pool.get('hr.holidays.status').browse(cr, uid, planned_id,context=context):
            sequence = record.sequence
        
        # Check adjust planned leave option is true or not
        if 'adjust_plannedleave' in values:  
            if values['adjust_plannedleave'] == True and sequence == 1:
                unplanned_id = self.pool.get('hr.holidays.status').search(cr, uid, [('sequence', '=', 2)], context=context)[0]
                values['holiday_status_id'] = unplanned_id
        
        
        #check employee notice period has started or not 
        # for record in self.pool.get('hr.holidays.status').browse(cr, uid, planned_id,context=context):
        #     leave_type = record.name
        # employee_obj = self.pool.get('hr.employee')
        # emp_ids = employee_obj.search(cr, uid, [('employee_no', '=like','AS%' )])
        # for emp in employee_obj.browse(cr, uid, emp_ids):
        #     if emp.emp_state  == 'on_notice' and str(leave_type) not in 'Loss Of Pay':
        #         raise osv.except_osv(_('Warning!'), _('Your notice period has started. You can apply only Loss of Pay leaves.'))

        # Remove time from date 
        if 'date_from' and 'date_to' in values:
            if values['date_from'] and values['date_to'] != False:
                values['date_from'] = (parser.parse(values['date_from'])).strftime("%Y-%m-%d")
                values['date_to'] = parser.parse(values['date_to']).strftime("%Y-%m-%d") 
         
        
        if 'type' in values:
            if values['type'] == 'remove':
                # Check if apply leave date month range is different then split leave
                date_from = parser.parse( values['date_from'])
                date_to = parser.parse(values['date_to'])
                start_date_month = date_from.month
                end_date_month = date_to.month


                if start_date_month != end_date_month:
                    res = self.split_leave(cr, uid, date_from, date_to, values)
                else:
                    res = osv.osv.create(self, cr, uid, values, context = None) 
            else:
                values['granted_date'] = datetime.datetime.now()
                #Add logger to display added value
                _logger.info(values)
                res = osv.osv.create(self, cr, uid, values, context = None) 

        #res = super(hr_holidays, self).create(cr, uid, values, context=None)
        try:
            # Send mail to reporting authority 
            if values['type'] == 'remove':
                template = self.pool.get('ir.model.data').get_object(cr, uid, 'hr_holidays_aspire', 'leave_request')
                mail_id = self.pool.get('mail.template').send_mail(cr, uid, template.id, res , force_send=True)
        except Exception, e:
            _logger.error('Email not send')
            _logger.error(str(e))
        return res

    # Override write method
    def write(self, cr, uid, ids, vals, context=None):
        flag = self.pool['res.users'].has_group(cr, uid, 'base.group_hr_reporting_authority')

        leave_record = self.browse(cr, uid, ids, context)          
        values = {}
        # Check only manager and reporting authority can approve leave
        if vals.get('state') and vals['state'] not in ['draft', 'confirm', 'cancel'] and not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_user') and not self.pool['res.users'].has_group(cr, uid, 'base.group_hr_reporting_authority') :
            raise osv.except_osv(_('Warning!'), _('You cannot set a leave request as \'%s\'. Contact a human resource manager.') % vals.get('state'))

        if 'date_from' in vals or 'date_to' in vals:
            for i in leave_record:
                date_from = False
                date_to = False
                from_session = False
                to_session = False
                if 'date_from' in vals and 'date_to' in  vals:
                    date_from = parser.parse(vals['date_from'])
                    date_to = parser.parse(vals['date_to'])
                elif 'date_from' in vals:
                    date_from = parser.parse(vals['date_from'])
                    date_to = parser.parse(leave_record['date_to'])
                elif 'date_to' in vals:
                    date_from = parser.parse(leave_record['date_from'])
                    date_to = parser.parse(vals['date_to'])
                
                if 'from_session' in vals:
                    from_session = vals['from_session']
                else:
                    from_session = leave_record['from_session']

                if 'to_session' in vals:
                    to_session = vals['to_session']
                else:
                    to_session = leave_record['to_session']

                start_date_month = date_from.month
                end_date_month = date_to.month

                if start_date_month != end_date_month:
                    values['message_follower_ids'] = False
                    values['employee_id'] = leave_record.employee_id.id
                    values['name'] = leave_record.name
                    values['sequence'] = leave_record.sequence
                    values['to_session'] = to_session
                    values['from_session'] = from_session
                    values['date_from'] = date_from
                    values['date_to'] = date_to
                    values['allocate_reasons'] = leave_record.allocate_reasons
                    values['message_ids'] = False
                    values['number_of_days_temp'] = False
                    values['holiday_status_id'] = leave_record.holiday_status_id.id
                    values['payslip_status'] = False
                    values['adjust_plannedleave'] = leave_record.adjust_plannedleave
                    values['carry_leave'] = leave_record.carry_leave
                    values['document'] = leave_record.document 
                    values['type'] = leave_record.type
                    values['notes'] = leave_record.notes
                    values['report_note'] = leave_record.report_note
                    values['category_id'] = leave_record.category_id
                    values['leave_id'] = leave_record.id
                    self.pool.get('hr.holidays').unlink(cr, uid, ids, context=None)

                    res = self.split_leave(cr, uid, date_from, date_to, values)
                    return True 
                else:
                    res = osv.osv.write(self, cr, uid, ids, vals, context = context) 
                    return res
        else:
            state = None
            res = False
            if 'state' in vals:
                # Get old state value
                state = self.get_state_value(cr, uid, ids, context = None)
                # Write current value on ids        
                res = osv.osv.write(self, cr, uid, ids, vals, context = context) 
             
                new_state = self.get_state_value(cr, uid, ids, context = None)        

            else:
                res = osv.osv.write(self, cr, uid, ids, vals, context = context) 


            # Post message in chatter_box
            if 'state' in vals:
                subject = False
                if vals['state'] == 'confirm':
                    subject = 'Request confirmed and waiting approval'
                elif vals['state'] == 'validate':
                    subject = 'Request approved'
                elif vals['state'] == 'refuse':
                    subject = 'Request refused'
                elif vals['state'] == 'cancel':
                    subject = 'Request cancelled'
                else:
                    subject = 'Leave request state changed'
                body = '%s --> %s' % (state, new_state)
                post_message = self.message_post(
                        cr, uid, ids,
                        body = str(body), subject = subject,
                        context=context)
            return res
            #return super(hr_holidays, self).write(cr, uid, ids, vals, context=context) 

    def get_state_value(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=None):
            state = record.state
            if state == 'confirm':
                state = 'To Approve'
            elif state == 'validate':
                state = 'Approved'
            elif state == 'cancel':
                state = 'Cancel'
            elif state == 'refuse':
                state = 'Refuse'
            elif state == 'draft':
                state = 'To Submit'
        return state
   
    # Overide parent method
    # Approve remove/add leave request by manager/officer/administrator
    def holidays_validate(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        self.write(cr, uid, ids, {'state':'validate'})
        data_holiday = self.browse(cr, uid, ids)
        for record in data_holiday:
            if record.double_validation:
                self.write(cr, uid, [record.id], {'manager_id2': manager})
            else:
                self.write(cr, uid, [record.id], {'manager_id': manager})
            
            if 'carry_leave' in record:
                if record.carry_leave == True:
                    continue    

            # Create calendar event in calendar.event model
            if record.holiday_type == 'employee' and record.type == 'remove':
                meeting_obj = self.pool.get('calendar.event')
                meeting_vals = {
                    'name': record.name or _('Leave Request'),
                    'categ_ids': record.holiday_status_id.categ_id and [(6,0,[record.holiday_status_id.categ_id.id])] or [],
                    'duration': record.number_of_days_temp * 8,
                    'description': record.notes,
                    'user_id': record.user_id.id,
                    'start': record.date_from,
                    'stop': record.date_to,
                    'allday': False,
                    'state': 'open',   # to block that meeting date in the calendar
                    'class': 'confidential',
                }   
                #Add the partner_id (if exist) as an attendee             
                if record.user_id and record.user_id.partner_id:
                    meeting_vals['partner_ids'] = [(4,record.user_id.partner_id.id)]
                    
                ctx_no_email = dict(context or {}, no_email=False)
                meeting_id = meeting_obj.create(cr, uid, meeting_vals, context={'type':'holiday'})

                # create leave in resource.calendar.leave
                self._create_resource_leave(cr, uid, [record], context=context)
                self.write(cr, uid, ids, {'meeting_id': meeting_id})

                try:
                    # Send mail to Parent for approve leave
                    compose_ctx = dict(context,active_ids=ids)
                    
                    if 'active_domain' in compose_ctx:
                        del compose_ctx['active_domain']
                    search_domain = [('name', '=', 'Leave Approved')]
                    template_id = self.pool['mail.template'].search(cr, uid, search_domain, context=context)[0]
                    compose_id = self.pool['mail.compose.message'].create(
                        cr, uid, {
                            'model': self._name,
                            'composition_mode': 'mass_mail',
                            'template_id': template_id,
                            'post': True,
                            'notify': True,
                        }, context=compose_ctx)
                    self.pool['mail.compose.message'].write(
                        cr, uid, [compose_id],
                        self.pool['mail.compose.message'].onchange_template_id(
                            cr, uid, [compose_id],
                            template_id, 'mass_mail', self._name, False,
                            context=compose_ctx)['value'],
                        context=compose_ctx)
                    self.pool['mail.compose.message'].send_mail(cr, uid, [compose_id], context=compose_ctx)
                except Exception, e:
                    _logger.error('Email not send')
                    _logger.error(str(e))

            # Create leave for all employee in particular category remove this functionality  new module
            elif record.holiday_type == 'category':
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [record.category_id.id])])
                leave_ids = []
                for emp in obj_emp.browse(cr, uid, emp_ids):
                    vals = {
                        'name': record.name,
                        'type': record.type,
                        'holiday_type': 'employee',
                        'holiday_status_id': record.holiday_status_id.id,
                        'date_from': record.date_from,
                        'date_to': record.date_to,
                        'notes': record.notes,
                        'number_of_days_temp': record.number_of_days_temp,
                        'parent_id': record.id,
                        'employee_id': emp.id,
                    }
                    leave_ids.append(self.create(cr, uid, vals, context=None))
                for leave_id in leave_ids:
                    # TODO is it necessary to interleave the calls?
                    for sig in ('confirm', 'validate', 'second_validate'):
                        self.signal_workflow(cr, uid, [leave_id], sig)
            recordData = record
            self.update_monthly_summary(cr, uid, ids,recordData, context=None)
        return True


    def update_monthly_summary(self, cr, uid, ids,recordData, context=None):
        if recordData and recordData.date_from:
            updateSql = 'UPDATE public.attendance_daily_summary SET "dailySumm_status"= False WHERE EXTRACT(MONTH FROM date)=' + str(datetime.datetime.strptime(recordData.date_from, DEFAULT_SERVER_DATETIME_FORMAT).month) + ' and EXTRACT(YEAR FROM date) = ' + str(datetime.datetime.strptime(recordData.date_from, DEFAULT_SERVER_DATETIME_FORMAT).year) + ' and emp_id = '+  str(recordData.employee_id.id) + ';'
            cr.execute(updateSql)

            deleteSql = 'DELETE FROM public.attendance_monthly_summary WHERE EXTRACT(MONTH FROM month) = ' + str(datetime.datetime.strptime(recordData.date_from, DEFAULT_SERVER_DATETIME_FORMAT).month) +  ' and EXTRACT(YEAR FROM month) = ' + str(datetime.datetime.strptime(recordData.date_from, DEFAULT_SERVER_DATETIME_FORMAT).year)  + ' and employee = ' + str(recordData.employee_id.id) + ';'

            cr.execute(deleteSql)

            self.pool.get('attendance.monthly.summary').attendance_monthly_summary_schedular(cr,uid,file_ids=None,context=None)



    # Split Leave
    # Count number of days in split leave
    def _get_days(self,cr,uid, from_dt, to_dt):
        """Returns a float equals to the timedelta between two dates given as string."""
        TOTAL_DAY = 0
        timedelta = to_dt.date() - from_dt.date()
        diff_day = timedelta.days + 1 
        for i in xrange(int(diff_day)):
            DATE = from_dt + datetime.timedelta(days=i)
            DATE = from_dt + datetime.timedelta(days=i)
            dataDate =  DATE.date()
            ids = []
            if self.check_working_day(cr,uid,ids,dataDate,context = None):
                TOTAL_DAY = TOTAL_DAY + 1
        return TOTAL_DAY

   
    # Get total days calculation for the split leaves
    def total_days(self, cr, uid, date_from, date_to, from_session, to_session):
       
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        number_of_days_temp = 0
        total_leave = 0
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'),_( Constant.INVALID_SESSION))

        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_days(cr,uid,date_from, date_to)
            holiday_leave = self.count_holiday_leave(cr, uid, date_from, date_to) 
            # Calculate holidays leave in apply leave by employee
            total_day = diff_day - holiday_leave
            total_leave = total_day
            if not from_session or not to_session :
                total_leave = total_day
            
            if (from_session and to_session) and from_session == 'session1' and to_session == 'session2':  
                total_leave = total_day
            
            check_start_date_holiday = self._check_start_end_holiday(cr, uid, str(date_from))
            if check_start_date_holiday != 0 and from_session == 'session2':
                total_leave = total_leave - 0.5

            ckeck_end_date_holiday = self._check_start_end_holiday(cr, uid ,str(date_to))
            if ckeck_end_date_holiday != 0 and to_session == 'session1':
                total_leave = total_leave - 0.5

            if total_day < 0:
                    total_leave = 0 
        return total_leave


    # Split leave
    def split_leave(self, cr, uid, date_from, date_to, values):
        leave_date = []
        from_session = False
        to_session = False
        leave_to_session = values['to_session']
        no_of_days =False
        time_delta = date_to.date() - date_from.date()
        diff_day = time_delta.days + 1
        from_dt = date_from
        to_dt = False
        for i in xrange(int(diff_day)):
            next_date = date_from + datetime.timedelta(days=i)
            if from_dt.month != next_date.month:
                to_dt = next_date - relativedelta(days=1)
                vals = {
                        'from_dt' : from_dt,
                        'to_dt': to_dt,
                }
                leave_date.append(vals)
                from_dt = next_date
        to_dt = date_to
        vals = {
            'from_dt' : from_dt,
            'to_dt': to_dt,
        }
        leave_date.append(vals)
        leave_date_range = len(leave_date)
        for i in xrange(leave_date_range):
            if i == 0:
                from_session = values['from_session']
                to_session = 'session2'
            elif i == (leave_date_range - 1):
                from_session = 'session1'
                to_session = leave_to_session
            else:
                from_session = 'session1'
                to_session = 'session2'
                      
            no_of_days = self.total_days(cr, uid, leave_date[i]['from_dt'], leave_date[i]['to_dt'] , from_session, to_session)
            if no_of_days == 0:
                continue
            values['from_session'] = from_session
            values['to_session'] = to_session
            values['date_from'] = leave_date[i]['from_dt']
            values['date_to'] = leave_date[i]['to_dt']
            values['number_of_days_temp'] = no_of_days
            res =  osv.osv.create(self, cr, uid, values, context = None) 
        return res

    # Override parent method
    def _create_resource_leave(self, cr, uid, leaves, context=None):
        '''This method will create entry in resource calendar leave object at the time of holidays validated '''
        obj_res_leave = self.pool.get('resource.calendar.leaves')
        for leave in leaves:
            vals = {
                'name': leave.name,
                'date_from': leave.date_from,
                'holiday_id': leave.id,
                'date_to': leave.date_to,
                'resource_id': leave.employee_id.resource_id.id,
                'calendar_id': leave.employee_id.resource_id.calendar_id.id
            }
            obj_res_leave.create(cr, uid, vals, context=context)
        return True
        return obj_res_leave.unlink(cr, uid, leave_ids, context=context)

    # Overide parent method
    # Cancel/Reject apply leave and add leave request
    def holidays_refuse(self, cr, uid, ids, context=None):
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        for holiday in self.browse(cr, uid, ids, context=context):
            if holiday.state == 'validate1':
                self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id': manager})
            else:
                self.write(cr, uid, [holiday.id], {'state': 'refuse', 'manager_id2': manager})
            if holiday.type != 'remove':
                continue
            self.holidays_cancel(cr, uid, ids, context=context)
            recordData = holiday
            self.update_monthly_summary(cr, uid, ids,recordData, context=None)
            # send mail to employee for reject leave application
            try:
                compose_ctx = dict(context,active_ids=ids)
                search_domain = [('name', '=', 'Leave Refused')]
                template_id = self.pool['mail.template'].search(cr, uid, search_domain, context=context)[0]
                compose_id = self.pool['mail.compose.message'].create(
                    cr, uid, {
                        'model': self._name,
                        'composition_mode': 'mass_mail',
                        'template_id': template_id,
                        'post': True,
                        'notify': True,
                    }, context=compose_ctx)
                self.pool['mail.compose.message'].write(
                    cr, uid, [compose_id],
                    self.pool['mail.compose.message'].onchange_template_id(
                        cr, uid, [compose_id],
                        template_id, 'mass_mail', self._name, False,
                        context=compose_ctx)['value'],
                    context=compose_ctx)
                self.pool['mail.compose.message'].send_mail(cr, uid, [compose_id], context=compose_ctx)
            except Exception, e:
                _logger.error('Email not send')
                _logger.error(str(e))
        return True

    
    # Overide parent method
    # Cancel/Reject leave request call from holiday_refuse function remove calender.event leave
    def holidays_cancel(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids):
            # Delete the meeting
            if record.meeting_id:
                record.meeting_id.unlink()

            # If a category that created several holidays, cancel all related
            self.signal_workflow(cr, uid, map(attrgetter('id'), record.linked_request_ids or []), 'refuse')

        self._remove_resource_leave(cr, uid, ids, context=context)
        return True

    # Override parent method
    # Remove resource leave function from holidays_cancel function
    def _remove_resource_leave(self, cr, uid, ids, context=None):
        '''This method will create entry in resource calendar leave object at the time of holidays cancel/removed'''
        obj_res_leave = self.pool.get('resource.calendar.leaves')
        leave_ids = obj_res_leave.search(cr, uid, [('holiday_id', 'in', ids)], context=context)

    # Cancel own leave request
    def holidays_cancel_own(self, cr, uid, ids, context=None):     
        obj_emp = self.pool.get('hr.employee')
        ids2 = obj_emp.search(cr, uid, [('user_id', '=', uid)])
        manager = ids2 and ids2[0] or False
        for holiday in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, [holiday.id], {'state': 'cancel', 'manager_id': manager})
        return True

    def forward_employee_leave(self, cr, uid, ids, context=None):
        # print '========++++++=========',self, cr, uid, ids[0]
        return {
            'name':_("Forward Employee Leave"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'forward.leave',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': '[]',
            'context': { 'leave_id':ids[0] },
        }


    @api.multi
    def action_approve_leave_request(self):
        data_obj = self.env['ir.model.data']
        if self._context.get('active_ids'):
            selected_records = self.search([('id','in',self._context.get('active_ids'))])
            for leaves in selected_records:
                if leaves.state == 'confirm': 
                    self.pool.get('hr.holidays').holidays_validate(self._cr, self._uid, [leaves.id], self._context)

class hr_employee(osv.osv):
    _inherit="hr.employee"

    def create(self, cr, uid, vals, context=None):
        # don't pass the value of remaining leave if it's 0 at the creation time, otherwise it will trigger the inverse
        # function _set_remaining_days and the system may not be configured for. Note that we don't have this problem on
        # the write because the clients only send the fields that have been modified.
        if 'remaining_leaves' in vals and not vals['remaining_leaves']:
            del(vals['remaining_leaves'])
        return super(hr_employee, self).create(cr, uid, vals, context=context)

    def _get_remaining_days(self, cr, uid, ids, name, args, context=None):
        # print "==== _get_remaining_days =====",ids, name, args
        cr.execute("""SELECT
                sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.limit=False and
                s.sequence=1 and
                h.employee_id in %s 
            group by h.employee_id""", (tuple(ids),))
        res = cr.dictfetchall()
        # print res
        remaining = {}
        for r in res:
            remaining[r['employee_id']] = r['days']
        for employee_id in ids:
            if not remaining.get(employee_id):
                remaining[employee_id] = 0.0
        return remaining

    def _get_unplanned_days(self, cr, uid, ids, name, args, context=None):
        # print "==== _get_remaining_days =====",ids, name, args
        cr.execute("""SELECT
                sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.limit=False and
                s.sequence=2 and
                h.employee_id in %s 
            group by h.employee_id""", (tuple(ids),))
        res = cr.dictfetchall()
        # print res
        remaining = {}
        for r in res:
            remaining[r['employee_id']] = r['days']
        for employee_id in ids:
            if not remaining.get(employee_id):
                remaining[employee_id] = 0.0
        return remaining

    def _get_floating_days(self, cr, uid, ids, name, args, context=None):
        # print "==== _get_remaining_days =====",ids, name, args
        cr.execute("""SELECT
                sum(h.number_of_days) as days,
                h.employee_id
            from
                hr_holidays h
                join hr_holidays_status s on (s.id=h.holiday_status_id)
            where
                h.state='validate' and
                s.limit=False and
                s.sequence=3 and
                h.employee_id in %s 
            group by h.employee_id""", (tuple(ids),))
        res = cr.dictfetchall()
        # print res
        remaining = {}
        for r in res:
            remaining[r['employee_id']] = r['days']
        for employee_id in ids:
            if not remaining.get(employee_id):
                remaining[employee_id] = 0.0
        return remaining
       
    def _leaves_count(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        leaves = self.pool['hr.holidays'].read_group(cr, uid, [
            ('employee_id', 'in', ids),
            ('holiday_status_id.limit', '=', False), ('state', '=', 'validate')], fields=['number_of_days', 'employee_id'], groupby=['employee_id'])
        res.update(dict([(leave['employee_id'][0], leave['number_of_days']) for leave in leaves ]))
        return res

    _columns = {
        'remaining_leaves': fields.function(_get_remaining_days, string='Planned Leaves', type="float", help='Total Plannaed Leaves', readonly=True),
        'remaining_unplanned_leaves': fields.function(_get_unplanned_days, string='Unplanned Leaves', type="float", help='Total Unplanned Leaves',readonly=True),
        'remaining_floating_leaves': fields.function(_get_floating_days, string='Floating Leaves',type="float", help='Total Floating Leaves',readonly=True),
        'leaves_count': fields.function(_leaves_count, type='float', string='Leaves'),
    }

class resource_calendar_leaves(osv.osv):
    _inherit = "resource.calendar.leaves"
    _name = "resource.calendar.leaves"


# # Calculate plannned/unplanned leave for old policy
# def calculate_leaves(total_leave):
#     result = {'value': {}}
#     leaves = int(total_leave / 4)
#     remindar = int(total_leave % 4)
#     planned_leave = leaves * 3 + remindar
#     unplanned_leave = leaves
#     result['value']['planned_leave'] = planned_leave
#     result['value']['unplanned_leave'] = unplanned_leave
#     return result


# New Calculate plannned/unplanned leave for old policy
def calculate_leaves(total_leave):
    result = {'value': {}}
    planned_leave = total_leave * (Constant.PLANNED_LEAVE_RATIO1/float(Constant.PLANNED_LEAVE_RATIO1 + Constant.PLANNED_LEAVE_RATIO2))
    rounded_planned_leave = 0.5 * math.ceil(planned_leave/0.5)
    unplanned_leave = total_leave - rounded_planned_leave
    result['value']['planned_leave'] = rounded_planned_leave
    result['value']['unplanned_leave'] = unplanned_leave
    return result

# Calculate leave as per new leave policy
def calculate_leaves_new(planned_leave,total_leave):
    result = {'value': {}}
    planned_leave =  (24 * planned_leave) / total_leave
    planned_leave = round(planned_leave)
    unplanned_leave = 24 - planned_leave
    result['value']['planned_leave'] = planned_leave
    result['value']['unplanned_leave'] = unplanned_leave
    return result
