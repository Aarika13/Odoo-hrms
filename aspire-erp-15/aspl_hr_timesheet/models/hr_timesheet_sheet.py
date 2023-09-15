from datetime import datetime, date, timedelta
from odoo.exceptions import UserError
from calendar import Calendar
import logging
import traceback
from odoo import api, fields, models,tools, _

_logger = logging.getLogger(__name__)


class hr_timesheet_sheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    # def _total(self):
    #     print("called total",self)
    #     """ Compute the attendances, analytic lines timesheets and differences between them
    #         for all the days of a timesheet and the current day
    #     """
    #     res = dict.fromkeys(self.ids, {
    #         'total_attendance': 0.0,
    #         'total_timesheet': 0.0,
    #         'total_difference': 0.0,
    #     })

    #     self._cr.execute("""
    #         SELECT sheet_id as id,
    #                sum(total_attendance) as total_attendance,
    #                sum(total_timesheet) as total_timesheet,
    #                sum(total_difference) as  total_difference
    #         FROM hr_timesheet_sheet_day
    #         WHERE sheet_id IN %s
    #         GROUP BY sheet_id
    #     """, (tuple(self.ids),))

    #     res.update(dict((x.pop('id'), x) for x in _cr.dictfetchall()))

    #     return res  
    
    
    
    
    
    # def create(self, vals):
    #     if 'employee_id' in vals:
    #         employee_id = vals['employee_id']
    #         new_user_id = self.env['hr.employee'].browse(employee_id).user_id
    #         if 'timesheet_ids' in vals and new_user_id:
    #             for record in vals['timesheet_ids']:
    #                 record[2]['user_id'] = new_user_id.id
    #                 record[2]['billable'] = True

    #         if not self.env['hr.employee'].browse(employee_id).user_id:
    #             raise UserError(_('In order to create a timesheet for this employee, you must link him/her to a user.'))

    #     if vals.get('attendances_ids'):
    #         # If attendances, we sort them by date asc before writing them, to satisfy the alternance constraint
    #         vals['attendances_ids'] = self.sort_attendances(vals['attendances_ids'])
    #     return super(hr_timesheet_sheet, self).create(vals)

    # def write(self, vals):
    #     if 'timesheet_ids' in vals:
    #         user_id = self.env['hr_timesheet_sheet.sheet'].browse(self.ids).employee_id.user_id.id
    #         if user_id:
    #             for record in vals['timesheet_ids']:
    #                 if record[2]:
    #                     if record[0] == 0:
    #                         account_id = record[2]['account_id']
    #                         emp_id = self.get_employee_id(user_id)
    #                         product = self.get_product_type(account_id, user_id)
    #                         display_name = self.get_display_name(account_id, user_id)
    #                         record[2]['user_id'] = user_id
    #                         record[2]['billable'] = True
    #                         if emp_id:
    #                             record[2]['employee_id'] = emp_id
    #                         if product:
    #                             record[2]['product_type'] = product
    #                         if display_name:
    #                             record[2]['display_name'] = display_name
    #         else:
    #             raise UserError(_('In order to create a timesheet for this employee, you must link him/her to a user.'))

    #     if 'employee_id' in vals:
    #         new_user_id = self.env['hr.employee'].browse(vals['employee_id']).user_id.id or False
    #         if not new_user_id:
    #             raise UserError(_('In order to create a timesheet for this employee, you must link him/her to a user.'))
    #         if not self._sheet_date(self.ids, forced_user_id=new_user_id):
    #             raise UserError(_('You cannot have 2 timesheets that overlap!\n'
    #                               'You should use the menu \'My Timesheet\' to avoid this problem.'))
    #         if not self.env['hr.employee'].browse(vals['employee_id']).product_id:
    #             raise UserError(
    #                 _('In order to create a timesheet for this employee, you must link the employee to a product.'))

    #     if vals.get('attendances_ids'):
    #         # If attendances, we sort them by date asc before writing them, to satisfy the alternance constraint
    #         # In addition to the date order, deleting attendances are done before inserting attendances
    #         vals['attendances_ids'] = self.sort_attendances(vals['attendances_ids'])
    #     res = super(hr_timesheet_sheet, self).write(vals)
    #     if vals.get('attendances_ids'):
    #         for timesheet in self.browse(self.ids):
    #             if not self.env['hr.attendance']._altern_si_so([att.id for att in timesheet.attendances_ids]):
    #                 raise UserError(_('Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)'))
    #     return res

    # def unlink(self):
    #     self._cr.execute('UPDATE hr_attendance SET sheet_id=Null WHERE sheet_id=' + str(self.ids[0]))
    #     return super(hr_timesheet_sheet, self).unlink(self.ids)

    # def get_employee_id(self, user_id):
    #     emp_obj = self.env['hr.employee'].search([('user_id', '=', user_id)]).id
    #     # user_obj_id = userObj.search([('user_id', '=', user_id)])
    #     # userObjData = userObj.browse(cr, uid, userObjId, context=context)
    #     # return userObjData.id
    #     return emp_obj

    # def get_product_type(self, account_id, user_id):

    #     project_obj = self.env['project.project'].search([('analytic_account_id', '=', account_id)])
    #     # project_obj_id = project_obj.search(cr, uid, [('analytic_account_id', '=', account_id)], context=context)
    #     # project_obj_data = project_obj_id.browse(cr, uid, project_obj_id, context)

    #     for ids in project_obj.member_id:
    #         if ids.name.id == user_id:
    #             if ids.product_type.id:
    #                 return ids.product_type.id
    #             else:
    #                 pass

    # def get_display_name(self, account_id, user_id):
    #     print("get_display_name")
    #     project_obj = self.env['project.project'].search([('analytic_account_id', '=', account_id)])
    #     # project_obj_id = project_obj.search([('analytic_account_id', '=', account_id)])
    #     # project_obj_data = project_obj_id.browse(project_obj_id)
    #     for ids in project_obj.member_id:
    #         if ids.name.id == user_id:
    #             return ids.display_name.id
    #         else:
    #             pass
    def link_timesheet_to_timesheet_sheet(self):
        timesheet_sheet_update = "update account_analytic_line aal set sheet_id = hts.id from hr_timesheet_sheet hts where hts.date_start <= aal.date and hts.date_end >= aal.date and aal.employee_id = hts.employee_id and aal.sheet_id is null;"
        self.env.cr.execute(timesheet_sheet_update)

    def approved_timesheet_activities(self):
        time_sheet_obj = self.env['hr_timesheet.sheet'].browse(self.ids)
        activity_obj = self.env['account.analytic.line']
        if time_sheet_obj:
            if time_sheet_obj.timesheet_ids:
                for activity in time_sheet_obj.timesheet_ids:
                    activity.write({'approved': True})
                self.write({'state': 'done'})

    def refuse_timesheet(self):
        if self.filtered(lambda sheet: sheet.state != "confirm"):
            raise UserError(_("Cannot reject a non-submitted sheet."))
        if self.filtered(lambda x: not x.can_review and x.review_policy == "hr"):
            raise UserError(_("Only a HR Officer or Manager can review the sheet."))
        self.write({"state": "draft", "reviewer_id": False})

    def button_confirm(self):    
        test = self.env['hr_timesheet.sheet'].reset_add_line()
        self.write({"state": "confirm"})

    # def get_employee_approval(self):
    #     print("called approval")
    #     return 15    
    
    #     time_sheet_obj = self.env['hr_timesheet.sheet']
    #     print("time_sheet_obj == ",time_sheet_obj)
    #     for sheet in self.browse(self.ids):
    #         print("sheet == ",sheet)
    #         if sheet.employee_id and sheet.employee_id.parent_id and sheet.employee_id.parent_id.user_id:
    #             # self.message_subscribe_users(cr, uid, [sheet.id], user_ids=[sheet.employee_id.parent_id.user_id.id], context=context)
    #             pass
    #         self.check_employee_attendance_state(sheet.id)
    #         di = sheet.user_id.company_id.timesheet_max_difference
    #         if (abs(sheet.total_difference) < di) or not di:
    #             print("called data")
    #             # time_sheet_obj.write(sheet.id, {'state': 'confirm'})
    #         else:
    #             raise UserError(_('Please verify that the total difference of the sheet is lower than %.2f.') % (di,))
    #     return True

    def add_next_month_my_timesheet(self):
        active_employee_data = self.env['hr.employee'].search([('with_organization','=',True)])
        today_obj = date.today()
        month_obj = int(today_obj.month)
        year_obj = today_obj.year

        cal = Calendar()
        weeks = cal.monthdayscalendar(year_obj, month_obj)
        try:
            for record in range(0, len(weeks)):
                last_day = 0
                first_day = 0
                if record == len(weeks) - 1:
                    for i in weeks[record]:
                        if i != 0:
                            last_day = i
                    first_day = weeks[record][0]
                else:
                    for i in weeks[record]:
                        if i != 0:
                            first_day = i
                            last_day = weeks[record][len(weeks[record]) - 1]
                            break

                start_month_date = datetime(year_obj, month_obj, first_day).date()
                end_month_date = datetime(year_obj, month_obj, last_day).date()
                try:
                    if active_employee_data:
        
                        for emp_rec in active_employee_data:
                            
                            if self.check_working_day(start_month_date, end_month_date,emp_rec.user_id):
                                
                                _logger.info("emp_rec == %s",emp_rec.name)
                                hr_timesheet_sheet_id = self.env['hr_timesheet.sheet'].search([('employee_id', '=', emp_rec.id),
                                                        ('date_start', '>=', start_month_date), 
                                                        ('date_end', '<=', end_month_date)])
                                
                                if not hr_timesheet_sheet_id:
                                    self.env['hr_timesheet.sheet'].create({
                                        'employee_id': emp_rec.id,
                                        'date_start': start_month_date,
                                        'date_end': end_month_date,
                                        'state': 'draft',
                                        'company_id': emp_rec.company_id.id,
                                    })
                        
                except Exception as e:
                    _logger.error('Something is wrong')
                    traceback.format_exc()
                    _logger.error(e)

        except Exception as e:
            _logger.error('Something is wrong')
            traceback.format_exc()
            _logger.error(e)
    

    # def approved_employee_my_timesheet(self):
    #     time_sheet_obj = self.env['hr_timesheet_sheet.sheet']
    #     # activity_obj = self.env['account.analytic.line']
    #     last_date = date.today() - timedelta(days=1)
    #     timesheet_ids = time_sheet_obj.search([('state', 'in', ['draft', 'confirm']), ('date_to', '<', last_date)])
    #     # , order='id asc'
    #     timesheet_data = time_sheet_obj.browse(timesheet_ids)
    #     for record in timesheet_data:
    #         count = 0
    #         if len(record.timesheet_ids) > 0:
    #             end_date = record.date_to
    #             temp_date = None
    #             for activity_data_obj in record.timesheet_ids:
    #                 if activity_data_obj.approved:
    #                     pass
    #                 else:
    #                     count += 1
    #             if count == 0 and end_date == temp_date:
    #                 time_sheet_obj.write(record.id, {'state': 'done'})
    #     return True

    def action_submit_to_manager(self):
        data_obj = self.env['ir.model.data']
        if self._context.get('active_ids'):   
            selected_records = self.search([('id', 'in', self._context.get('active_ids'))])
            for timesheet in selected_records:
                if timesheet.state == 'draft':
                    timesheet.button_confirm()

    def action_approve_timesheet(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        group_of_own_employee = self.env['res.groups'].sudo().search([('users','=',user.id),('full_name','ilike','own timesheets')])
        if self._context.get('active_ids'):
            selected_records = self.search([('id', 'in', self._context.get('active_ids'))])
            for timesheet in selected_records:
                if group_of_own_employee and user.employee_id == timesheet.employee_id:
                    raise UserError(_("Employee Could not approve own timesheet"))
                if timesheet.state == 'confirm':
                    timesheet.approved_timesheet_activities()

    def check_working_day(self, start_date, end_date, user_id):
        is_working = False
        diff = end_date - start_date
        for single_date in (start_date + timedelta(n) for n in range(diff.days + 1)):
            # public_holiday_leave_object = self.env['resource.calendar.leaves']
            # domain = [('holiday_from', '=', single_date)]
            n_holidays = self.env['resource.calendar.leaves'].search([('date_from', '=', single_date)])
            if len(n_holidays) == 0:
                date_code = self.get_day_code(single_date)
                res_company_data = self.env['res.company'].search([('id','=',user_id.company_id.id)])
                if res_company_data:
                    return True

                # print("sql_data == ",sql_data)
                # sql = 'SELECT "' + date_code + '" FROM public.res_company where id = ' + str(user_id.company_id.id)
                # print("sql == ",sql)
                # self._cr.execute(sql)
                # rows = self._cr.fetchall()
                # print("row == ",rows)
                # for i in rows[0]:
                #     if i:
                #         is_working = True
                #         return True
        return False

    def get_day_code(self, data_date):
        first_day = data_date.replace(day=1)
        dom = data_date.day
        remainder = dom % 7
        week_int = dom / 7
        if remainder > 0:
            week_int = week_int + 1
        return 'W' + str(week_int) + data_date.strftime("%A")[:3]

# class hr_timesheet_sheet_day(models.Model):
#     _name = "hr_timesheet.sheet.day"
#     _description = "Timesheets by Period"
#     _auto = False

#     name: fields.Date('Date', readonly=True)
#     sheet_id: fields.Many2one('hr_timesheet.sheet', 'Sheet', readonly=True, select="1")
#     total_timesheet: fields.Float('Total Timesheet', readonly=True)
#     total_attendance: fields.Float('Attendance', readonly=True)
#     total_difference: fields.Float('Difference', readonly=True)

#     def init(self):
#         tools.drop_view_if_exists(self._cr, 'hr_timesheet_sheet_day')
#         self._cr.execute("""create or replace view hr_timesheet_sheet_day as
#             SELECT
#                 id,
#                 name,
#                 sheet_id,
#                 total_timesheet,
#                 total_attendance,
#                 cast(round(cast(total_attendance - total_timesheet as Numeric),2) as Double Precision) AS total_difference
#             FROM
#                 ((
#                     SELECT
#                         MAX(id) as id,
#                         name,
#                         sheet_id,
#                         timezone,
#                         SUM(total_timesheet) as total_timesheet,
#                         CASE WHEN SUM(orphan_attendances) != 0
#                             THEN (SUM(total_attendance) +
#                                 CASE WHEN current_date <> name
#                                     THEN 1440
#                                     ELSE (EXTRACT(hour FROM current_time AT TIME ZONE 'UTC' AT TIME ZONE coalesce(timezone, 'UTC')) * 60) + EXTRACT(minute FROM current_time AT TIME ZONE 'UTC' AT TIME ZONE coalesce(timezone, 'UTC'))
#                                 END
#                                 )
#                             ELSE SUM(total_attendance)
#                         END /60  as total_attendance
#                     FROM
#                         ((
#                             select
#                                 min(l.id) as id,
#                                 p.tz as timezone,
#                                 l.date::date as name,
#                                 s.id as sheet_id,
#                                 sum(l.unit_amount) as total_timesheet,
#                                 0 as orphan_attendances,
#                                 0.0 as total_attendance
#                             from
#                             	account_analytic_line l
#                                 LEFT JOIN hr_timesheet_sheet s ON s.id = l.sheet_id
#                                 JOIN hr_employee e ON s.employee_id = e.id
#                                 JOIN resource_resource r ON e.resource_id = r.id
#                                 LEFT JOIN res_users u ON r.user_id = u.id
#                                 LEFT JOIN res_partner p ON u.partner_id = p.id
#                             group by l.date::date, s.id, timezone
#                         ) union (
#                             select
#                                 -min(a.id) as id,
#                                 p.tz as timezone,
#                                 (a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))::date as name,
#                                 s.id as sheet_id,
#                                 0.0 as total_timesheet,
#                                 SUM(CASE WHEN a.action = 'sign_in' THEN -1 ELSE 1 END) as orphan_attendances,
#                                 SUM(((EXTRACT(hour FROM (a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))) * 60) + EXTRACT(minute FROM (a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC')))) * (CASE WHEN a.action = 'sign_in' THEN -1 ELSE 1 END)) as total_attendance
#                             from
#                                 hr_attendance a
#                                 LEFT JOIN hr_timesheet_sheet s
#                                 ON s.id = a.sheet_id
#                                 JOIN hr_employee e
#                                 ON a.employee_id = e.id
#                                 JOIN resource_resource r
#                                 ON e.resource_id = r.id
#                                 LEFT JOIN res_users u
#                                 ON r.user_id = u.id
#                                 LEFT JOIN res_partner p
#                                 ON u.partner_id = p.id
#                             WHERE a.action in ('sign_in', 'sign_out')
#                             group by (a.name AT TIME ZONE 'UTC' AT TIME ZONE coalesce(p.tz, 'UTC'))::date, s.id, timezone
#                         )) AS foo
#                         GROUP BY name, sheet_id, timezone
#                 )) AS bar""")

