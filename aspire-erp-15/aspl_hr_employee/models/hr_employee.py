# -*- coding: utf-8 -*-
import logging
from dateutil import parser
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, date
import traceback
import calendar
from ..constant.constant import Constant
from ..common.validation import Validation
import numpy as np
from odoo.exceptions import ValidationError
from odoo.addons.web.controllers.main import DataSet
from odoo.models import check_method_name
from odoo.api import call_kw
from odoo.http import request
from odoo.exceptions import UserError
import math
from datetime import timedelta 
from docxtpl import DocxTemplate,InlineImage
from htmldocx import HtmlToDocx
import jinja2
import os
import io
import base64
import zipfile
from docxcompose.composer import Composer
from docx import Document


_logger = logging.getLogger(__name__)

RELATION = [
    ('husband', 'Husband'),
    ('wife', 'Wife'),
    ('daughter', 'Daughter'),
    ('son', 'Son'),
    ('brother', 'Brother'),
    ('sister', 'Sister'),
    ('mother', 'Mother'),
    ('father', 'Father'),
]

SEPARATION_MODE = [
    ('awol', 'ABSENT W/O LEAVE'),
    ('contract_expire', 'CONTRACT EXPIRE'),
    ('absconding', 'ABSCONDING'),
    ('expired', 'EXPIRED'),
    ('others', 'OTHERS'),
    ('resigned', 'RESIGNED'),
    ('retired', 'RETIRED'),
    ('sick', 'SICK'),
    ('terminated', 'TERMINATED'),
    ('transferred', 'TRANSFERRED'),
]

EMPLOYMENT_TYPE = [
    ('permanent_employee', 'Permanent Employee'),
    ('temporary_employee', 'Temporary Employee'),
    ('trainee', 'Trainee'),
    ('consultant', 'Consultant'),
]


# Calculate employee leave
def cal_leave(join_date, total_leave, leave_interval):
    join_date = parser.parse(str(join_date))
    day = join_date.day
    month = join_date.month
    d = 0
    quarter = (12 - month) / 3.0

    quarter_int = int(quarter)

    quarter_diff = quarter - quarter_int
    if 'MONTHLY' in str(leave_interval).upper():
        if day <= 15:
            d = total_leave
        else:
            if total_leave > 1:
                d = total_leave - 1
            else:
                d = 0
    else:
        if quarter_diff > 0.5 or quarter_diff > 0 and day <= 15:
            d = 1
        elif quarter_diff > 0 and day > 15:
            d = 0.5
        else:
            d = 0
    if 'MONTHLY' in str(leave_interval).upper():
        add_leave = d
    else:
        add_leave = floor((quarter_int + d) * total_leave * 3 / 12.0, 0.5)
    return add_leave


def floor(x, s):
    return s * math.floor(float(x) / s)


class Employee(models.Model):
    _inherit = 'hr.employee'

    grey_gratuity = fields.Float("Grey Gratuity", tracking=True)
    emp_gratuity = fields.Float("EMP Gratuity",compute="_compute_emp_gratuity")

    @api.depends('slip_ids','payslip_count')
    def _compute_emp_gratuity(self):
        for rec in self:
            payslip_line_ids = self.env['hr.payslip.line'].search(
                [('code', '=', 'GRATUITY'), ('employee_id', '=', rec.id)])
            total_gratuity = rec.grey_gratuity
            if payslip_line_ids:
                 total_gratuity += sum(payslip_line_ids.mapped('amount'))
            rec.emp_gratuity = total_gratuity

    # TODO If above compute works the delete these code.
    # @api.onchange('user_id')
    # def onchange_user_id(self):
    #     print("\nonchange_user_id called\n")
    #     print(self.user_id.id, self.id)
    #     if self.user_id:
    #         self.user_id.employee_id = int(str(self.id).split('_')[-1])

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super(Employee, self).create(vals_list)
    #     print("\n-----------------------------Create_Called------------------\n")
    #     vals_list[0]['is_employee'] = True
    #     vals_list[0]['active_employee'] = True
    #     vals_list[0]['is_candidate'] = False
    #     vals_list[0]['is_applicant'] = False
    #     print(vals_list)
    #     stop_create
    #     return res

    def get_attach_id(self,record):
        url = self.env['ir.config_parameter'].get_param('web.base.url')

        if record == 'birth_day_notification':
            attachment_id_face_to_face = self.env.ref('aspl_hr_employee.birthday_image_record').sudo().id
        elif record == '2_year_complete_notification':
            attachment_id_face_to_face = self.env.ref('aspl_hr_employee.2_work_anniversary_image_record').sudo().id
        elif record == '5_year_complete_notification':
            attachment_id_face_to_face = self.env.ref('aspl_hr_employee.5_work_anniversary_image_record').sudo().id
        elif record == '10_year_complete_notification':
            attachment_id_face_to_face = self.env.ref('aspl_hr_employee.10_work_anniversary_image_record').sudo().id

        return url, attachment_id_face_to_face

    def _get_mail_to(self,record):
        mail_to_list_temp = []

        if ( record != '2_year_complete_notification' and record != '5_year_complete_notification' and record != '10_year_complete_notification' ):
            mail_to_list_temp.append(self.parent_id.work_email)
            mail_to_list_temp.append(self.coach_id.work_email)

        attendance_manager_group_users = self.env['res.users'].search(
            [('groups_id', '=', self.env.ref('hr_attendance.group_hr_attendance_manager').sudo().id)])
        hr_employee = self.env['hr.employee'].search(
            [('user_id', 'in', attendance_manager_group_users.ids), ('department_id.name', '=', 'HR & Admin'),
             ('user_id.company_ids', 'in', self.company_id.id)])
        for mail in hr_employee: mail_to_list_temp.append(mail.work_email)

        mail_to_list = list(set(mail_to_list_temp))

        if False in mail_to_list:
            mail_to_list.remove(False)

        if ( record == '2_year_complete_notification' or record == '5_year_complete_notification' or record == '10_year_complete_notification'):
            mail_to = mail_to_list[0]
        else:
            mail_to = ','.join(mail_to_list)

        return mail_to

    # def _get_mail_to_all(self):
    #     company_id = [1,2]
    #     hr_employee = self.env['hr.employee'].sudo().search([('with_organization', '=', True), ('company_id', 'in', company_id)])
    #     mail_to_all = hr_employee.mapped('work_email')
    #
    #     mail_to_all = list(set(mail_to_all))
    #
    #     if False in mail_to_all:
    #         mail_to_all.remove(False)
    #
    #     mail_to = ','.join(mail_to_all)
    #     return mail_to

    # Need to uncomment after script run
    def _get_actual_experience(self):
        for rec in self:
            if rec.resume_line_ids:
                experience_in_day = 0
                for data in rec.resume_line_ids:
                    if data.line_type_id.name == "Experience":
                        if rec.resume_line_ids:
                            for previousEmployment in data:
                                ds = datetime.strftime(previousEmployment.date_start, '%Y:%m:%d')                              
                                if previousEmployment.date_end:
                                    de = datetime.strftime(previousEmployment.date_end, '%Y:%m:%d')
                                    experience_in_day = int((datetime.strptime(de, '%Y:%m:%d') - datetime.strptime(
                                        ds, '%Y:%m:%d')).days) + experience_in_day

                                else:
                                    experience_in_day = int(
                                                (datetime.now().date() - datetime.strptime(ds,'%Y:%m:%d').date()).days) + experience_in_day

                # if rec.join_date:
                #     dt = datetime.strftime(rec.join_date, '%Y:%m:%d')
                #     # print("actual_experience_record_join ==== ",dt)
                #     if rec.join_date and datetime.strptime(dt,
                #                                             "%Y:%m:%d").date() < datetime.now().date():
                #         # print("experience_in_day >>>>>>>>>>>...",experience_in_day)
                #         experience_in_day = int(
                #             (datetime.now().date() - datetime.strptime(dt,'%Y:%m:%d').date()).days) + experience_in_day
                #         # print("current date",datetime.now().date())
                #         # print("older date",datetime.strptime(dt,'%Y:%m:%d').date())
                #         # print("actual_experience_experience_in_day ==== ",experience_in_day)
                year = experience_in_day // 365
                month = (experience_in_day % 365) // 30
                exp = ""
                if year == 1:
                    exp = exp + str(year) + " Year "
                if year > 1:
                    exp = exp + str(year) + " Years "   
                if month == 1:
                    exp = exp + str(month) + " Month"
                if month > 1:
                    exp = exp + str(month) + " Months"    
                rec.actual_experience = exp
            else:
                rec.actual_experience = 0

    def _get_relative_experience(self):
        for rec in self:
            if rec.resume_line_ids:
                experience_in_day = 0
                for data in rec.resume_line_ids:
                    if data.line_type_id.name == "Experience": 
                        if rec.resume_line_ids:
                            for previous_employment in data:
                                
                                if previous_employment.relevant:
                                    ds = datetime.strftime(previous_employment.date_start, '%Y:%m:%d')
                                    if previous_employment.date_end:
                                        de = datetime.strftime(previous_employment.date_end, '%Y:%m:%d')
                                        experience_in_day = int((datetime.strptime(de, '%Y:%m:%d') - datetime.strptime(
                                            ds, '%Y:%m:%d')).days) + experience_in_day 

                                    else:
                                        experience_in_day = int(
                                            (datetime.now().date() - datetime.strptime(ds,'%Y:%m:%d').date()).days) + experience_in_day
                # if rec.join_date:
                #     dt = datetime.strftime(rec.join_date, '%Y:%m:%d')
                #     print("relative_experienc_dt_join_date === ",dt)
                #     if rec.join_date and datetime.strptime(dt,
                #                                             "%Y:%m:%d").date() < datetime.now().date():
                #         experience_in_day = int(
                #             (datetime.now().date() - datetime.strptime(dt,
                #                                                         '%Y:%m:%d').date()).days) + experience_in_day
                #         print("relative_experienc_join_date_experience_in_day ==== ",experience_in_day)
                year = experience_in_day // 365
                month = (experience_in_day % 365) // 30
                exp = ""

                if year == 1:
                    exp = exp + str(year) + " Year "
                if year > 1:
                    exp = exp + str(year) + " Years "
                if month == 1:
                    exp = exp + str(month) + " Month"
                if month > 1:
                    exp = exp + str(month) + " Months"
                rec.relative_experience = exp
            else:
                rec.relative_experience = 0

    def _get_experience_graduation(self):
        for rec in self:
            experience_in_day = 0
            graduation_data = []
            if rec.resume_line_ids:
                for emp_education in rec.resume_line_ids:
                    if emp_education.line_type_id.name == 'Education' and emp_education.date_end:
                        de = datetime.strftime(emp_education.date_end, '%Y:%m:%d')
                        experience_in_day = int((datetime.now().date() - datetime.strptime(de, '%Y:%m:%d').date()).days)
                        graduation_data.append(experience_in_day)  
            if len(graduation_data) == 0:
                graduation_data.append(0)

            experience_in_day = min(graduation_data)
            year = experience_in_day // 365
            month = (experience_in_day % 365) // 30
            exp = ""
            
            if year == 1:
                exp = exp + str(year) + " Year "
            if year > 1:
                exp = exp + str(year) + " Years "
            if month == 1:
                exp = exp + str(month) + " Month"
            if month > 1:
                exp = exp + str(month) + " Months"
            rec.experience_graduation = exp

    def get_week_of_month(self, year, month, day):
        x = np.array(calendar.monthcalendar(year, month))
        week_of_month = np.where(x == day)[0][0] + 1
        return (week_of_month)

    # Calculate reference name from application id
    def _compute_reference_name(self):
        for record in self:
            try:
                applicant_obj = self.env['hr.applicant'].search([('emp_id', '=', record.id)])
                for data in applicant_obj:
                    if data.emp_id and data.partner_id:
                        record.reference_name = data.partner_id.name
            except Exception as e:
                _logger.error('Something is wrong')
                _logger.error(str(e))
                traceback.format_exc()

    # Calculate reference end date based on grade of employee
    def _compute_reference_end_date(self):
        for record in self:
            try:
                applicant_obj = self.env['hr.applicant'].search([('emp_id', '=', record.id)])
                for data in applicant_obj:
                    if data.emp_id and data.partner_id:
                        if record.join_date:
                            if record.grade:
                                add_months = 6
                                if record.grade.sequence == 1:
                                    record.reference_end_date = None
                                elif record.grade.sequence > 3:
                                    add_months = 12
                                reference_end_date = parser.parse(record.join_date) + relativedelta(
                                    months=+add_months)
                                record.reference_end_date = reference_end_date
            except Exception as e:
                _logger.error('Something is wrong')
                _logger.error(str(e))
                traceback.format_exc()

    # TODO: If needed when have the right employee numbers are available.
    # def update_company_history(self):
    #     active_emp_ids = self.env['hr.employee'].search([('id', '=', 7)])
    #     print("\n", active_emp_ids, len(active_emp_ids))
    #     for emp in active_emp_ids:
    #         print(emp.company_id.id, emp.employee_no, emp.employee_no_type, emp.create_date)
    #         if emp.position_company:
    #             for rec in emp.position_company:
    #                 if rec.company_id.id == emp.company_id.id:
    #                     rec.employment_type = emp.employee_no_type
    #                     rec.employee_no = emp.employee_no
    #         else:
    #             emp.position_company.company_id = emp.company_id.id
    #             emp.position_company.employee_no = emp.employee_no
    #             emp.position_company.employment_type = emp.employee_no_type
    #             emp.position_company.effective_from = emp.create_date


    # Employee joining details
    company_id = fields.Many2one('res.company', required=False)
    v9_id = fields.Integer('Employee ID from V9')
    emp_state = fields.Selection(
        [('new', 'New'), ('training', 'Training'), ('probation', 'Probation'), ('confirmed', 'Confirmed'),
         ('on_notice', 'On Notice Period'), ('left', 'Left Organization')], 'Status', readonly=True, default='new', tracking=True)
    state_name = fields.Char("State Name", compute="_state_name")
    trainee_no = fields.Char("Trainee Code", readonly=True,tracking=True)
    join_training_date = fields.Date('Training start date',tracking=True)
    training_period = fields.Integer('Training Period', help='Enter months', default="0",tracking=True)
    training_end_date = fields.Date(string="Training End Date",tracking=True)
    join_date = fields.Date('Join Date',tracking=True)
    probation_period = fields.Integer('Probation Period', help="Enter months", default="3",tracking=True)
    probation_end_date = fields.Date('Probation End Date',tracking=True)
    confirm_date = fields.Date('Confirmed Date',tracking=True)
    notice_period = fields.Integer('Notice Period', help="Enter months", default="3",tracking=True)
    appraisal_date = fields.Date('Appraisal Due On',tracking=True)
    # Employee Number
    employee_type_edit = fields.Boolean('Employee Type Edit')
    employee_no_type = fields.Selection([
        ('permanent_employee', 'Permanent Employee'),
        ('consultant_aspire', 'Consultant Aspire'),
        ('trainee', 'Trainee'),
        ('temporary_employee', 'Temporary Employee'),
        ('client', 'Client'),
        ('consultant_other', 'Consultant Other')
    ], 'Employment Type', help="Select Employment Type",tracking=True)
    # employee_no_type = fields.Char("Employment type",readonly=True)
    # Need to add compute after creating employee from Odoo 9
    employee_no = fields.Char("Employee No", store=True, readonly=True) # employment_type Moved to position history
    v9_employee_no = fields.Char("V9 Employee No", readonly=True)
    # Personal Details
    marriage_date = fields.Date(string='Marriage Date',tracking=True)
    father = fields.Char(string='Father')
    spouse = fields.Char(string='Spouse')
    religion = fields.Char(string='Religion',tracking=True)
    international_employee = fields.Boolean(string='International Employee',tracking=True)
    physically_challenged = fields.Boolean('Physically Challenged',tracking=True)
    blood_group = fields.Selection(
        [('o+', 'O+'),
         ('o-', 'O-'),
         ('a+', 'A+'),
         ('a-', 'A-'),
         ('b+', 'B+'),
         ('b-', 'B-'),
         ('ab+', 'AB+'),
         ('ab-', 'AB-')], string='Blood Group',tracking=True)
    skype_id = fields.Char(string='Skype Id', size=30)
    isPresentAddSameAsPermanent = fields.Boolean(string='Same as Permanent Address')
    personal_email = fields.Char(string='Personal Email', size=240, required=True,tracking=True)
    # Experience fields
    actual_experience = fields.Char(compute='_get_actual_experience', string='Actual Experience')
    relative_experience = fields.Char(compute='_get_relative_experience', string='Relative Experience')
    experience_graduation = fields.Char(compute='_get_experience_graduation',
                                        string='Experience From Graduation')
    color = fields.Integer(string='Color Index')
    # leave_in_notice = fields.Char(compute='_get_leave_in_notice', string='Leave in notice period')

    # Employee Address
    pre_street = fields.Char('Present Street',tracking=True)
    pre_landmark = fields.Char('Present Landmark',tracking=True)
    pre_city = fields.Char('Present City', size=30, help='City max size is 30',tracking=True)
    pre_pcode = fields.Char('Present Pin code', size=6, help='Pincode max size is 6',tracking=True)
    pre_state = fields.Many2one('res.country.state', 'Present State',tracking=True)
    pre_county = fields.Many2one('res.country', 'Present Country',tracking=True)
    pre_phone1 = fields.Char('Present Mobile No',tracking=True)
    pre_phone2 = fields.Char('Present Phone No',tracking=True)
    per_street = fields.Char('Permanent Street', required=True,tracking=True)
    per_landmark = fields.Char('Permanent Landmark',tracking=True)
    per_city = fields.Char('Permanent City', size=30, help="City max size is 30", required=True,tracking=True)
    per_pcode = fields.Char('Permanent Pin code', size=6, help='Pincode max size is 6', required=True,tracking=True)
    per_state = fields.Many2one('res.country.state', 'Permanent State', required=True,tracking=True)
    per_county = fields.Many2one('res.country', 'Permanent Country', required=True,tracking=True)
    per_phone1 = fields.Char('Permanent Mobile No',tracking=True)
    per_phone2 = fields.Char('Permanent Phone No',tracking=True)

    # Employee other_info
    # bank_account_id inherited from hr.employee
    bank_account_ids = fields.Many2one('hr.bank.detail', 'Bank Name', help="Bank detail")
    bank_id = fields.Many2one('res.bank')
    account_type_id = fields.Selection([
        ('salary', 'Salary'),
        ('saving', 'Saving'),
        ('current', 'Current')
    ], 'Account type', help='Add employee bank account type')
    bank_record_name = fields.Char('Name as per bank record',tracking=True)
    bank_account_no = fields.Char('Account Number', size=20, help="Max size 20",tracking=True)
    pf_employee = fields.Boolean('Employee covered under of PF',tracking=True)
    uan = fields.Char('UAN', size=12,tracking=True)
    pf_number = fields.Char('PF Number', help="Ex.: AA/AAA/1234567/123/1234567",tracking=True)
    pf_date = fields.Date('PF Join Date',tracking=True)
    family_pf_no = fields.Char('Family PF No', size=50,tracking=True)
    esi_employee = fields.Boolean('Include ESI',tracking=True)
    esi_no = fields.Char('ESI Number', size=50,tracking=True)

    # Employee identity
    employee_identity_id = fields.One2many('employee.identity', 'employee_id', 'Employee Identity', required=False)

    # Employee education detail
    # education_id = fields.One2many('employee.education', 'employee_id', 'Employee Education', required=True)

    # Employee family detail
    family_member_id = fields.One2many('family.member', 'employee_id', 'Family Members', required=False,tracking=True)

    # Passport & Visa information
    # passport_id = fields.One2many('employee.passport', 'employee_id', 'Passport Information', required=False)
    # visa_id = fields.One2many('employee.visa', 'employee_id', 'Visa Information', required=False)

    # Employee Document
    employee_document_id = fields.One2many('employee.document', 'employee_id', 'Document Detail')
    employee_document_previous_id = fields.One2many('employee.document', 'employee_id', 'Document Detail',domain=[('type','=','past')])
    employee_document_current_id = fields.One2many('employee.document', 'employee_id', 'Document Detail',domain=[('type','=','current')])
    employee_document_education_id = fields.One2many('employee.document', 'employee_id', 'Document Detail',domain=[('type','=','education')])
    # Previous employment
    # previous_employmnet_id = fields.One2many('previous.employment', 'employee_id', 'Previous Employment')

    # Access card detail
    access_card_id = fields.One2many('access.card.detail', 'employee_id', 'Access Card Detail')

    # Nomination detail
    nomination_id = fields.One2many('nomination.detail', 'employee_id', 'Nomination Detail')

    # Position history
    position_designation = fields.One2many('designation.history', 'employee_id', 'Designation', required=True,tracking=True)
    position_location = fields.One2many('location.history', 'employee_id', 'Location',tracking=True)
    position_department = fields.One2many('department.history', 'employee_id', 'Department Name', required=True,tracking=True)
    position_grade = fields.One2many('grade.history', 'employee_id', 'Grade',tracking=True)
    position_division = fields.One2many('division.history', 'employee_id', 'Division',tracking=True)
    position_cost = fields.One2many('cost.history', 'employee_id', 'Cost',tracking=True)
    position_reporting = fields.One2many('reporting.history', 'employee_id', 'Reporting To',tracking=True)
    position_company = fields.One2many('company.history', 'employee_id', 'Company',tracking=True)

    # Employee resign
    separation_mode = fields.Selection(SEPARATION_MODE, 'Separation Mode')
    employee_left = fields.Boolean('Employee left organization',tracking=True)
    left_date = fields.Date('Date',tracking=True)
    remarks = fields.Text('Remarks')
    exitRemark = fields.Text('Exit Remarks')
    demise = fields.Date('Date Of Demise')
    retired_date = fields.Date('Retirement Date',tracking=True)

    # Appraisal
    appraisal_ids = fields.One2many('employee.appraisal', 'employee_id', 'Appraisal Detail',tracking=True)

    # Resignation
    resignation_date = fields.Date('Resignation Submitted On',tracking=True)
    leaving_rason = fields.Selection(
        [('abandoned', 'ABANDONED'), ('contect expire', 'CONTRACT EXPIRE'), ('deported', 'DEPORTED'),
         ('expired', 'EXPIRED'), ('others', 'OTHERS'), ('resigned', 'RESIGNED'), ('retired', 'RETIRED'),
         ('sick', 'SICK'), ('terminated', 'TERMINATED'), ('transferred', 'TRANSFERRED'),
         ('termination', 'TERMINATION ON LEAVE')], 'Reason For Leaving',tracking=True)
    notice_required = fields.Boolean('Notice Required', default=True,tracking=True)
    resigned_notice_period = fields.Integer('Resigned Notice Period',tracking=True)
    short_notice_period = fields.Float('Short Fall in Notice Period',tracking=True)
    tentative_leaving_date = fields.Date('Tentative Leaving Date',tracking=True)
    interview_date = fields.Date('Interview Date',tracking=True)
    note = fields.Text('Note',tracking=True)
    leaving_date = fields.Date('Leaving Date',tracking=True)
    settled_date = fields.Date('Settled Date',tracking=True)
    left_org = fields.Boolean('Employee Has Left The Organization',tracking=True)
    notice_served = fields.Boolean('Notice Served',tracking=True)
    rehired = fields.Boolean('Fit To Rehired',tracking=True)

    # Calculate employee complete 6 month after joining date
    reference_end_date = fields.Date(compute='_compute_reference_end_date', string='Reference End Date',
                                     help='Calculate after 6 month date from joining date of employee',
                                     store=True)
    reference_name = fields.Char(compute='_compute_reference_name', string='Reference Name',
                                 help='Get Reference name from application', store=True)

    # Employee left organization
    contracted = fields.Boolean('Contracted')
    with_organization = fields.Boolean('Active With Organization', default=True,tracking=True)
    biometric_no = fields.Char("Biometric Code", size=10,tracking=True)
    history = fields.Text('History')
    offer_letter_file = fields.Binary(string="Offer Letter",readonly=True,required = False)
    work_email = fields.Char('Work Email',tracking=True)
    department_id = fields.Many2one('hr.department', 'Department', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    parent_id = fields.Many2one('hr.employee', 'Manager', compute="_compute_parent_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    coach_id = fields.Many2one(
        'hr.employee', 'Coach', compute='_compute_coach', store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help='Select the "Employee" who is the coach of this employee.\n'
             'The "Coach" has no specific rights or responsibilities by default.',tracking=True)
    
    address_id = fields.Many2one('res.partner', 'Work Address', compute="_compute_address_id", store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    
    work_location_id = fields.Many2one('hr.work.location', 'Work Location', compute="_compute_work_location_id", store=True, readonly=False,
        domain="[('address_id', '=', address_id), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    
    resource_calendar_id = fields.Many2one('resource.calendar', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    tz = fields.Selection(
        string='Timezone', related='resource_id.tz', readonly=False,
        help="This field is used in order to define in which timezone the resources will work.",tracking=True)
    
    employee_type = fields.Selection([
        ('employee', 'Employee'),
        ('student', 'Student'),
        ('trainee', 'Trainee'),
        ('contractor', 'Contractor'),
        ('freelance', 'Freelancer'),
        ], string='Employee Type', default='employee', required=True,tracking=True,
        help="The employee type. Although the primary purpose may seem to categorize employees, this field has also an impact in the Contract History. Only Employee type is supposed to be under contract and will have a Contract History.")
    
    job_id = fields.Many2one('hr.job', 'Job Position', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",tracking=True)
    
    barcode = fields.Char(string="Badge ID", help="ID used for employee identification.", groups="hr.group_hr_user", copy=False,tracking=True)
    # birthday_this_year = fields.Date("Birthday This Year")
    # update_resume_line = fields.Boolean(compute = "change_hr_resume_line",string = 'Change Resume line depend on Leaving Date',required =False)
    # @api.model
    # def create(self, values):
    #     """ We don't want the current user to be follower of all created job """
    #     hr_emp = super(Employee)
    #     self._compute_employee_no() /home/aspire110/Project/aspire-erp-15/aspl_hr_employee

    @api.onchange('leaving_date')
    def change_hr_resume_line(self):
        for rec in self:
            last_update = []
            if rec.resume_line_ids:
                for data in rec.resume_line_ids:
                    if data.line_type_id.name =="Experience":
                        last_update.append(data._origin.write_date)
                max_date = max(last_update)
                for data in rec.resume_line_ids:
                    if data.line_type_id.name == "Experience" and not data.date_end:
                        data.write({'date_end':self.leaving_date})
                    elif data.line_type_id.name == "Experience" and data.write_date == max_date:
                        data.write({'date_end':self.leaving_date})
    
    def _adjust_timeoff_manager(self):
        record_data = self.env['hr.employee'].search([('leave_manager_id', '=', self.id)])
        for record in record_data:
            manager_employee = record.parent_id
            manager_res_user = manager_employee.user_id
            record.write({'leave_manager_id':manager_res_user.id})

            # leave_manager_res_user = record.leave_manager_id
            # leave_manager_employee = leave_manager_res_user.employee_id

            # if leave_manager_employee.employee_left or not leave_manager_res_user:
            #     manager_employee = record.parent_id
            #     manager_res_user = manager_employee.user_id
            #     # self.write({'leave_manager_id':manager_res_user.id})
              
    # def _get_birthday_month(self):
    #     month = self.birthday.strftime('%m')
    #     self.birthday_month = month

    # @api.model
    # def _compute_birthday(self):
    #     # print("employee data == ",self)
    #     for employee in self:
    #         now = fields.Datetime.now()
    #         employee_id = self.env['hr.employee'].browse(employee.id)
    #         date = employee_id.birthday
    #         if date and not employee_id.employee_left:
    #             now = now.replace(day=date.day,month=date.month)
    #         else:
    #             now = now.replace(year=1000)

    #         # print("date == ",now)    
    #         employee.birthday_this_year = now

    def cron_celebration_meeting(self):
        # print("print",self)
        employee_id = self.env['hr.employee'].search([])
        # print("employee_id == ",employee_id)
        for employee in employee_id:
            start = fields.Datetime.now()
            stop = fields.Datetime.now()
            date_b = employee.birthday
            date_m = employee.marriage_date
            date_j = employee.join_date
            
            if employee.emp_state == 'left':
                birthday_event_left = self.env['calendar.event'].search([('name','ilike','Birthday'),('res_id','=',employee.id)])
                birthday_event_left.unlink()
                    
            elif  date_b and not employee.employee_left:
                start = start.replace(day=date_b.day,month=date_b.month,hour=0,minute=0,second=0)
                stop = start.replace(day=date_b.day,month=date_b.month,hour=10,minute=59,second=59)
 
                birthday_count = self.env['calendar.event'].search([('res_id','=',employee.id),('start','=',start),('name','ilike','Birthday')])
                birthday_event = self.env['calendar.event']

                #_logger.info("employee" , employee)
                if not birthday_count:
                    vals = {
                        'name': employee.name + " - Birthday",
                        'res_id':employee.id,
                        'res_model':'hr.employee',
                        'start' : start,
                        'stop': stop,
                        }
                    birthday_event.create(vals)

            if employee.emp_state == 'left':
                marriage_event_left = self.env['calendar.event'].search([('name','ilike','Marriage Anniversery'),('res_id','=',employee.id)])
                marriage_event_left.unlink()
            
            elif  date_m and not employee.employee_left and date_m.year != start.year:
                start = start.replace(day=date_m.day,month=date_m.month,hour=0,minute=0,second=0)
                stop = start.replace(day=date_m.day,month=date_m.month,hour=10,minute=59,second=59)

                marriage_count = self.env['calendar.event'].search([('res_id','=',employee.id),('start','=',start),('name','ilike','Marriage Anniversery')])
                marriage_event = self.env['calendar.event']

                if not marriage_count:
                    vals = {
                        'name': employee.name + " - Marriage Anniversery",
                        'res_id':employee.id,
                        'res_model':'hr.employee',
                        'start' : start,
                        'stop': stop,
                        }
                    marriage_event.create(vals)

            if employee.emp_state == 'left':
                joining_event_left = self.env['calendar.event'].search([('name','ilike','Joining Anniversery'),('res_id','=',employee.id)])
                joining_event_left.unlink()

            elif  date_j and not employee.employee_left and date_j.year != start.year:
                start = start.replace(day=date_j.day,month=date_j.month,hour=0,minute=0,second=0)
                stop = start.replace(day=date_j.day,month=date_j.month,hour=10,minute=59,second=59)

                joining_count = self.env['calendar.event'].search([('res_id','=',employee.id),('start','=',start),('name','ilike','Joining Anniversery')])
                joining_event = self.env['calendar.event']

                if not joining_count:
                    vals = {
                        'name': employee.name + " - Joining Anniversery",
                        'res_id':employee.id,
                        'res_model':'hr.employee',
                        'start' : start,
                        'stop': stop,
                        }
                    joining_event.create(vals)
        

                
    def letter(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'employee.letter.wizard',
            'view_type':'form',
            'view_mode':'form',
            'name':_('Employee Letter'),
            'target':'new',
            'context': {'employee_id': [self.id]},
        }
    
    def _state_name(self):
        self.state_name = 'New' if self.emp_state == 'new' else 'Training' \
            if self.emp_state == 'training' else 'Probation' if self.emp_state == 'probation' else 'Notice' \
            if self.emp_state == 'on_notice' else 'Confirmed' if self.emp_state == 'confirmed' else 'Left Organization' \
            if self.emp_state == 'left' else ''

    @api.onchange('training_period')
    def on_change_training_period(self):
        for record in self:
            if record.training_period == 0:
                record.training_end_date = record.join_training_date
                record.join_date = record.join_training_date
            elif record.training_period and record.join_training_date:
                record.training_end_date = record.join_training_date + relativedelta(
                    months=record.training_period)
                record.join_date = record.training_end_date + relativedelta(days=1)

    @api.onchange('probation_period')
    def on_change_probation_period(self):
        for record in self:
            if record.probation_period == 0:
                record.confirm_date = record.join_date
            elif record.probation_period and record.join_date:
                record.probation_end_date = record.join_date + relativedelta(
                    months=record.probation_period)

    @api.onchange('join_date')
    def on_change_join_date(self):
        for record in self:
            if record.probation_period and record.join_date:
                record.probation_end_date = record.join_date + relativedelta(
                    months=record.probation_period)
                record.appraisal_date = record.join_date + relativedelta(months=12)

    @api.onchange('join_training_date')
    def on_change_join_training_date(self):
        for record in self:
            if record.training_period == 0:
                record.join_date = record.join_training_date
            elif record.training_period and record.join_training_date:
                record.training_end_date = record.join_training_date + relativedelta(
                    months=record.training_period)
                record.join_date = record.training_end_date + relativedelta(days=1)


    @api.onchange('probation_end_date')
    def on_change_probation_end_date(self):
        for record in self:
            if record.probation_end_date:
                record.confirm_date = record.probation_end_date + relativedelta(days=1)

    @api.onchange('notice_period')
    def onchange_notice_period(self):
        return {'value': {'resigned_notice_period': self.notice_period}}

    @api.onchange('resigned_notice_period')
    def on_change_resigned_notice_period(self):
        for record in self:
            if record.resignation_date:
                dt = datetime.strftime(record.resignation_date, "%Y:%m:%d")
                record.tentative_leaving_date = datetime.strptime(dt, "%Y:%m:%d") + relativedelta(
                    months=record.resigned_notice_period)

    @api.onchange('resignation_date')
    def on_change_resignation_date(self):
        for record in self:
            if record.resignation_date:
                dt = datetime.strftime(record.resignation_date, "%Y:%m:%d")
                record.tentative_leaving_date = datetime.strptime(dt, "%Y:%m:%d") + relativedelta(
                    months=record.resigned_notice_period)

    @api.onchange('leaving_date')
    def on_change_leaving_date(self):
        for rec in self:
            short_fall_in_day = 0
            if rec.emp_state == 'on_notice' and rec.separation_mode == 'resigned' and rec.tentative_leaving_date and rec.leaving_date:
                tld = datetime.strftime(rec.tentative_leaving_date, "%Y:%m:%d")
                ld = datetime.strftime(rec.leaving_date, "%Y:%m:%d")
                short_fall_in_day = int((datetime.strptime(tld, "%Y:%m:%d") - datetime.strptime(ld, "%Y:%m:%d")).days)

                tentative_leaving_date = datetime.strptime(tld, "%Y:%m:%d").date()
                leaving_date = datetime.strptime(ld, "%Y:%m:%d").date()
                day_diff = tentative_leaving_date.weekday() - leaving_date.weekday()

                days = ((tentative_leaving_date - leaving_date).days - day_diff) / 7 * 5 + min(day_diff, 5) - (
                        max(tentative_leaving_date.weekday() - 4, 0) % 5)

                if leaving_date.month == tentative_leaving_date.month:
                    if self.get_week_of_month(leaving_date.year, leaving_date.month,
                                              leaving_date.day) == 1 and leaving_date.weekday() <= 5:
                        days = days + 1
                else:
                    if self.get_week_of_month(tentative_leaving_date.year, tentative_leaving_date.month,
                                              tentative_leaving_date.day) > 1:
                        days = days + 1
                    if self.get_week_of_month(tentative_leaving_date.year, tentative_leaving_date.month,
                                              tentative_leaving_date.day) == 1 and tentative_leaving_date.weekday() == 5:
                        days = days + 1
                    if self.get_week_of_month(leaving_date.year, leaving_date.month,
                                              leaving_date.day) == 1 and leaving_date.weekday() <= 5:
                        days = days + 1
                    if (tentative_leaving_date.month - leaving_date.month) > 1:
                        days = days + (tentative_leaving_date.month - leaving_date.month) - 1
                short_fall_in_day = days
                # TODO : Need to fix after hr_holiday module migration
                if rec.resignation_date and rec.leaving_date and rec.tentative_leaving_date and rec.user_id:
                    holiday_leave = self.count_holiday_leave(rec.resignation_date, rec.leaving_date)
                    if 'type' in self.env['hr.leave']._fields:
                        applied_leave = self.count_applied_leave(rec.resignation_date, rec.tentative_leaving_date,
                                                                rec.user_id)
                        rec.short_notice_period = short_fall_in_day + holiday_leave + applied_leave
                    else:
                        rec.short_notice_period = short_fall_in_day + holiday_leave    

    def count_holiday_leave(self, from_date, to_date):
        n_holidays = 0
        try:
            domain = [
                ('holiday_from', '<=', to_date),
                ('holiday_from', '>=', from_date),
            ]
            n_holidays = self.env['resource.calendar.leaves'].search_count(domain)
        except ValueError:
            return False
        return n_holidays

    def count_applied_leave(self, from_date, to_date, user_id):
        emp_id = self.env['hr.employee'].search([('user_id', '=', user_id.id)])
        leave_id = self.env['hr.leave'].search([
            ('employee_id', '=', emp_id.id),
            ('date_from', '>=', from_date),
            ('type', '=', 'remove'),
        ])  # , ('type', '=', 'remove')
        number_of_days = 0
        for leaves in leave_id:
            number_of_days += (leaves.number_of_days * -1)  # = number_of_days +
        return number_of_days

    def on_notice(self):
        # hr_obj = self.env['hr.employee'].browse(self.ids)
        if self.notice_period > 0:
            self.write({'emp_state': 'on_notice', 'color': 4})
            # Send mail on changing emp_state to Notice Period
            # compose_ctx = dict(context, active_ids=ids)
            # Need to add email template
            search_domain = [('name', '=', 'Mail for Employee State Changed to Notice Period')]
            template_id = self.env['mail.template'].search(search_domain)
            compose_id = self.env['mail.compose.message'].create({
                'model': self._name,
                'composition_mode': 'mass_mail',
                'template_id': template_id.id,
                'notify': True,
            })
            compose_id._action_send_mail(compose_id.id)
        else:
            raise ValidationError(_('Please Enter "Notice Period"'))
        return True

    def confirmed(self):
        if self.employee_left:
            hr_obj = self.env['hr.employee'].browse(self.ids)
            separation_details = 'Separation Mode: ' + str(
                hr_obj.separation_mode) + '\n' + 'Resignation Submitted On: ' + str(
                hr_obj.resignation_date) + '\n' + 'Reason For Leaving: ' + str(
                hr_obj.leaving_rason) + '\n' + 'Remarks: ' + '\n' + str(hr_obj.remarks) + '\n' + str(
                hr_obj.left_date) + '\n' + 'Left Date: ' + str(hr_obj.left_date)
            hr_obj.write({
                'emp_state': 'confirmed',
                'color': 8,
                'history': separation_details,
                'employee_left': False,
                'with_organization': True
            })
            user_obj = self.env['res.users'].search([('id', '=', hr_obj.user_id.id)])
            user_obj.write({
                'active': True
            })
            # Send mail on changing emp_state to Notice Period
            # search_domain = [('name', '=', 'Mail for Employee State Changed to Notice Period')]
            # template_id = self.env['mail.template'].search(search_domain)[0]
            # compose_id = self.env['mail.compose.message'].create({
            #         'model': self._name,
            #         'composition_mode': 'mass_mail',
            #         'template_id': template_id,
            #         'post': True,
            #         'notify': True,
            #     })
            # self.env['mail.compose.message'].write(
            #     [compose_id],
            #     self.env['mail.compose.message'].onchange_template_id(
            #         [compose_id],
            #         template_id, 'mass_mail', self._name, False))
            # self.env['mail.compose.message'].send_mail(cr, uid, [compose_id], context=compose_ctx)
        # else:
        #     raise Warning(_('Please Enter "Notice Period"'))
        else:
            # Add unplanned leave for confirm employee
            confirm_date = self.confirm_date
            if confirm_date:
                dt = datetime.strftime(self.confirm_date, '%Y:%m:%d')
                if datetime.strptime(dt, '%Y:%m:%d').date() <= datetime.today().date():
                    self.write({'emp_state': 'confirmed', 'color': 8})
                    self.employee_left = False
                    self.with_organization = True
                    current_year = datetime.now().year
                    if current_year != 2015:
                        try:
                            holiday_type = self.env['hr.leave.type'].search([('active', '=', True)])
                            if 'sequence' in self.env['hr.leave.type']._fields:
                                unplanned_leave = self.add_employee_leaves(2, confirm_date)
                                floating_leave = self.add_employee_leaves(3, confirm_date)
                        except Exception as e:
                            _logger.error('Something is wrong')
                            _logger.error(str(e))
                            traceback.format_exc()
                    # Send mail on changing emp_state to Confirm
                    search_domain = [('name', '=', 'Mail for Employee State Changed to Confirm')]
                    template_id = self.env['mail.template'].search(search_domain)
                    compose_id = self.env['mail.compose.message'].create({
                        'model': self._name,
                        'composition_mode': 'mass_mail',
                        'template_id': template_id,
                        # 'post': True,
                        'notify': True,
                    })
                    # compose_id.write(
                    #     self.pool['mail.compose.message'].onchange_template_id(
                    #         cr, uid, [compose_id],
                    #         template_id, 'mass_mail', self._name, False,
                    #         context=compose_ctx)['value'],
                    #     context=compose_ctx)
                    compose_id._action_send_mail(compose_id.id)
                else:
                    raise ValidationError(_('Please Enter correct "Confirm Date"'))
            else:
                raise ValidationError(_('Please Enter "Confirm Date"'))

        return True

    def training(self):
        if self.employee_left:
            hr_obj = self.env['hr.employee'].browse(self.ids)
            separation_details = 'Separation Mode: ' + str(
                hr_obj.separation_mode) + '\n' + 'Resignation Submitted On: ' + str(
                hr_obj.resignation_date) + '\n' + 'Reason For Leaving: ' + str(
                hr_obj.leaving_rason) + '\n' + 'Remarks: ' + '\n' + str(hr_obj.remarks) + '\n' + str(
                hr_obj.left_date) + '\n' + 'Left Date: ' + str(hr_obj.left_date)
            hr_obj.write({
                'emp_state': 'training',
                'history': separation_details,
                'employee_left': False,
                'with_organization': True
            })
            user_obj = self.env['res.users'].search([('id', '=', hr_obj.user_id.id)])
            user_obj.write({
                'active': True
            })
        else:
            if self.join_training_date:
                dt = datetime.strftime(self.join_training_date, '%Y:%m:%d')
            else:
                dt = datetime.strftime(datetime.now().date(), '%Y:%m:%d')
                self.write({'join_training_date':datetime.now().date()})

            # else:
            #     # raise RuntimeWarning('Please Enter "Training start date"!!')
            if self.training_period > 0:
                confirm_date = str(self.join_training_date)
                if datetime.strptime(dt, "%Y:%m:%d").date() <= datetime.today().date():
                    self.write({'emp_state': 'training', 'color': 9})
                    # Send mail on changing emp_state to Training
                    search_domain = [('name', '=', 'Mail for Employee State Changed to Training')]
                    template_id = self.env['mail.template'].search(search_domain)
                    compose_id = self.env['mail.compose.message'].create({
                        'model': self._name,
                        'composition_mode': 'mass_mail',
                        'template_id': template_id,
                        # 'post': True,
                        'notify': True,
                    })
                    # compose_id.write(
                    #     cr, uid, [compose_id],
                    #     self.pool['mail.compose.message'].onchange_template_id(
                    #         cr, uid, [compose_id],
                    #         template_id, 'mass_mail', self._name, False,
                    #         context=compose_ctx)['value'],
                    #     context=compose_ctx)
                    self.env['mail.compose.message']._action_send_mail(compose_id.id)
                else:
                    raise ValidationError(_('Please Enter correct "Training start date"'))
            else:
                raise ValidationError(_('Please Enter "Training Period"!!'))
            #     raise ValidationError(_('Please Enter "Training start date"!!'))
        return True

    def probation(self):
        if self.employee_left:
            hr_obj = self.env['hr.employee'].browse(self.ids)
            separation_details = 'Separation Mode: ' + str(
                hr_obj.separation_mode) + '\n' + 'Resignation Submitted On: ' + str(
                hr_obj.resignation_date) + '\n' + 'Reason For Leaving: ' + str(
                hr_obj.leaving_rason) + '\n' + 'Remarks: ' + '\n' + str(hr_obj.remarks) + '\n' + str(
                hr_obj.left_date) + '\n' + 'Left Date: ' + str(hr_obj.left_date)
            self.write({
                'emp_state': 'probation',
                'color': 6,
                'history': separation_details,
                'employee_left': False,
                'with_organization': True
            })
            user_obj = self.env['res.users'].search([('id', '=', hr_obj.user_id.id)])
            user_obj.write({
                'active': True
            })
            # Send mail on changing emp_state to Notice Period
            # compose_ctx = dict(context, active_ids=ids)
            # search_domain = [('name', '=', 'Mail for Employee State Changed to Notice Period')]
            # template_id = self.pool['mail.template'].search(cr, uid, search_domain, context=context)[0]
            # compose_id = self.pool['mail.compose.message'].create(
            #     cr, uid, {
            #         'model': self._name,
            #         'composition_mode': 'mass_mail',
            #         'template_id': template_id,
            #         'post': True,
            #         'notify': True,
            #     }, context=compose_ctx)
            # self.pool['mail.compose.message'].write(
            #     cr, uid, [compose_id],
            #     self.pool['mail.compose.message'].onchange_template_id(
            #         cr, uid, [compose_id],
            #         template_id, 'mass_mail', self._name, False,
            #         context=compose_ctx)['value'],
            #     context=compose_ctx)
            # self.pool['mail.compose.message'].send_mail(cr, uid, [compose_id], context=compose_ctx)
        # else:
        #     raise Warning(_('Please Enter "Notice Period"'))
        else:
            if self.join_date:
                if self.probation_period > 0:
                    if self.emp_state == 'new':
                        self.write({'emp_state': 'probation', 'color': 6})
                        self.employee_left = False
                        self.with_organization = True
                        join_date = self.join_date
                        current_year = datetime.now().year
                        if current_year != 2015:
                            try:
                                # if str(self.employee_no_type).lower() == "trainee":
                                    # employee_no = self.pool.get('ir.sequence').get(cr, uid,'hr.permanent.employee')
                                # self.write({'trainee_no': self.employee_no})
                                if self.employee_no_type != 'consultant':
                                    self.write({'employee_no_type': 'permanent_employee'})
                                    # self.position_company.write({'employment_type':'permanent_employee'})
                                holiday_type = self.env.get('hr.leave.type').search(
                                    [('active', '=', True)],
                                )
                                if 'sequence' in self.env['hr.leave.type']._fields:
                                    planned_leave = self.add_employee_leaves(1, join_date)
                            except Exception as e:
                                _logger.error('Something is wrong')
                                _logger.error(str(e))
                                traceback.format_exc()
                    
                    elif self.join_training_date:
                        dt = datetime.strftime(self.join_training_date, '%Y:%m:%d')
                        if datetime.strptime(dt, '%Y:%m:%d').date() <= datetime.today().date():
                            self.write({'emp_state': 'probation', 'color': 6})
                            self.employee_left = False
                            self.with_organization = True
                            join_date = self.join_date
                            current_year = datetime.now().year
                            if current_year != 2015:
                                try:
                                    if str(self.employee_no_type).lower() == "trainee":
                                        # employee_no = self.pool.get('ir.sequence').get(cr, uid,'hr.permanent.employee')
                                        self.write({'trainee_no': self.employee_no})
                                        if self.employee_no_type != 'consultant':
                                            self.write({'employee_no_type': 'permanent_employee'})
                                            # self.position_company.write({'employment_type':'permanent_employee'})
                                    holiday_type = self.env.get('hr.leave.type').search(
                                        [('active', '=', True)],
                                    )
                                    if 'sequence' in self.env['hr.leave.type']._fields:
                                        planned_leave = self.add_employee_leaves(1, join_date)
                                except Exception as e:
                                    _logger.error('Something is wrong')
                                    _logger.error(str(e))
                                    traceback.format_exc()
                    else:
                        raise ValidationError(_('Please Enter correct "Joining start date"'))
                else:
                    raise ValidationError(_('Please Enter "Probation Period"!!'))
            else:
                raise ValidationError(_('Please Enter "Probation start date"!!'))

            # Send mail on changing emp_state to Probation
            # search_domain = [('name', '=', 'Mail for Employee State Changed to Probation')]
            # template_id = self.env['mail.template'].search(search_domain)
            # compose_id = self.env['mail.compose.message'].create({
            #     'model': self._name,
            #     'composition_mode': 'mass_mail',
            #     'template_id': template_id.id,
            #     'post': True,
            # 'notify': True,
            # })
            # compose_id.write(self.pool['mail.compose.message'].onchange_template_id(
            #         cr, uid, [compose_id],
            #         template_id, 'mass_mail', self._name, False,
            #         context=compose_ctx)['value'],
            #     context=compose_ctx)
            # self.env['mail.compose.message']._action_send_mail(compose_id.id)
        return True

    # Employee with organization change false with change in separation mode
    def on_left_org(self):
        # res = {'value': {}}
        # if self.employee_left:
        #     id = str(self.id)[-2:]
        #     # record = self.env['hr.employee'].search([('parent_id', '=', self.id)])
        #     employee_obj = self.env['hr.employee'].search([('id', '=', int(id))])
        #     # employee_obj.write({'emp_state': 'left'})
        #     # userObj = self.pool.get('res.users')
        #     # empObjId = empObj.search(cr,uid,[('id','in',ids)],context=context)
        #     # empObjData = empObj.browse(cr,uid,empObjId,context)
        #     # userObjId = userObj.search(cr,uid,[('id','=',empObjData.user_id.id)],context=context)
        #     # userObjData = userObj.browse(cr,uid,userObjId,context=context)
        #     # userObjData.write({'active':False})
        #     return {'value': {'with_organization': False, 'emp_state': 'left'}}
        # else:
        #     return {'value': {'active': True, 'with_organization': True, 'emp_left': False}}
        employee_obj = self.env['hr.employee'].search([('id', '=', self.ids)])
        employee_obj.write({
            'emp_state': 'left',
            'with_organization': False,
            'employee_left': True,
        })
        user_obj = self.env['res.users'].search([('id', '=', employee_obj.user_id.id)])
        user_obj.write({
            'active': False
        })
        if 'active_employee' in self.env['res.partner']._fields:
            active_emp_partner_obj = self.env['res.partner'].search([('active_employee', '=', True)])
            for de_active_partner in active_emp_partner_obj:
                de_active_partner.write({'active_employee': False})
            active_emp_ids = self.env['hr.employee'].search([('with_organization', '=', True)]).ids
            active_users = self.env['res.users'].search([('employee_id', 'in', active_emp_ids)])
            for active in active_users:
                partner_obj = self.env['res.partner'].search([('email', '=', active.login)])
                partner_obj.write({'active_employee': True})
                 
        if 'reviewer_user_ids' in self.env['hr.applicant']._fields:
            employee_user = self.user_id
            applicant_obj = self.env['hr.applicant'].search([('reviewer_user_ids', '=', employee_user.id)])
            for applicant in applicant_obj:
                applicant_reviewer = applicant.reviewer_user_ids
                
                if len(applicant_reviewer) <= 1: 
                    applicant_recruiter = applicant.user_id
                    applicant.write({'reviewer_user_ids':applicant_recruiter})
                    applicant.write({'interviewers_ids':applicant_recruiter})

                if len(applicant_reviewer) > 1:
                    for multi_reviewer in applicant_reviewer:
                        if multi_reviewer.id == employee_user.id:
                            applicant.write({'reviewer_user_ids':[(3,multi_reviewer.id)]})
                            applicant.write({'interviewers_ids':[(3,multi_reviewer.id)]})

        #Changes of time off officer on left
        if 'leave_manager_id' in self.env['hr.employee']._fields:
            self._adjust_timeoff_manager()

        # return {'value': {'employee_left': True,'with_organization': False, 'active': False, 'emp_state': 'left'}}

    def add_employee_leaves(self, leave_sequence, confirm_date):
        employee_obj = self.env['hr.employee']
        holiday_type_obj = self.env['hr.leave.type']
        holiday_obj = self.env['hr.leave.allocation']

        # Holiday leave id
        holiday_type_id = holiday_type_obj.search([('sequence', '=', leave_sequence)])
        if not holiday_type_id:
            return False

        # holiday_type_data = holiday_type_obj.browse(holiday_type_id)
        total_leave = holiday_type_id.no_leave
        if leave_sequence == 1:
            diff = date.today().month - parser.parse(str(confirm_date)).month + 1
            total_leave = total_leave * diff
        leave_interval = holiday_type_id.add_interval
        add_leave = cal_leave(confirm_date, total_leave, leave_interval)
        if add_leave:
            holiday_type_id = holiday_type_id and holiday_type_id[0] or False
            leave_ids = []  # For add leaves
            for emp in employee_obj.browse(self.ids):
                vals = {
                    'name': _('Allocation for %s') % emp.name,
                    'state': 'validate',
                    'employee_id': emp.id,
                    'holiday_status_id': holiday_type_id.id,
                    'type': 'add',
                    'holiday_type': 'employee',
                    'number_of_days': add_leave,
                    'multi_employee': True,
                    'adjust_planned_leave': False,
                    # 'date_from': holiday_obj.granted_date,
                    # 'date_to': holiday_obj.month_end,

                }
                leave_ids.append(holiday_obj.create(vals))
                # for leave_id in leave_ids:
                #     # TODO is it necessary to interleave the calls?
                #     for sig in ('confirm', 'validate', 'second_validate'):
                #         holiday_obj.signal_workflow([leave_id], sig)
            return True
        else:
            return False

    @api.onchange('isPresentAddSameAsPermanent')
    def on_change_is_Present_Add_Same_As_Permanent(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_street = record.per_street
                record.pre_landmark = record.per_landmark
                record.pre_city = record.per_city
                record.pre_pcode = record.per_pcode
                record.pre_state = record.per_state
                record.pre_county = record.per_county
                record.pre_phone1 = record.per_phone1
                record.pre_phone2 = record.per_phone2
            else:
                record.pre_street = None
                record.pre_landmark = None
                record.pre_city = None
                record.pre_pcode = None
                record.pre_state = None
                record.pre_county = None
                record.pre_phone1 = None
                record.pre_phone2 = None

    @api.onchange('per_street')
    def on_change_pre_street(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_street = record.per_street

    @api.onchange('per_landmark')
    def on_change_per_landmark(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_landmark = record.per_landmark

    @api.onchange('per_city')
    def on_change_per_city(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_city = record.per_city

    @api.onchange('per_pcode')
    def on_change_per_pcode(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_pcode = record.per_pcode

    @api.onchange('per_state')
    def on_change_per_state(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_state = record.per_state

    @api.onchange('per_county')
    def on_change_per_county(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_county = record.per_county

    @api.onchange('per_phone1')
    def on_change_per_phone1(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_phone1 = record.per_phone1

    @api.onchange('per_phone2')
    def on_change_per_phone2(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_phone2 = record.per_phone2

    @api.constrains('work_email', 'per_phone1', 'personal_email')
    def _check_constraints(self):
        if self.per_phone1:
            flag = Validation.check_phone(self.per_phone1)
            if not flag:
                raise ValidationError(Constant.INVALID_MOBILE_NO)
        if self.work_email:
            flag = Validation.check_email(self.work_email)
            if not flag:
                raise ValidationError(Constant.INVALID_WORK_EMAIL)
        if self.personal_email:
            flag = Validation.check_email(self.personal_email)
            if not flag:
                raise ValidationError(Constant.INVALID_PERSONAL_EMAIL)     
        return True 


    def current_employee_form(self):
        exist = self.sudo().search([["user_id", "=", self.env.uid]], limit=1)

        view_id = self.env['ir.ui.view'].search([('name','=','hr.own.employee.form')])
        
        return {
            "type" : "ir.actions.act_window",
            "res_model" : 'hr.employee',
            "view_mode": "form", 
            "name":_('Information'),
            "view_id":view_id.id,
            "res_id": exist.id if exist.id else False
        }           


class StDataSet(DataSet):
    # Odoo Core Web Module method override for manage own access in employee
    def _call_kw(self, model, method, args, kwargs):
        if model == 'hr.employee' and method == 'read':
            group_hr_manager = request.env.user.has_group('hr.group_hr_manager')
            # group_hr_officer = request.env.user.has_group('hr.group_hr_user')
            employees = request.env['hr.employee'].browse(args[0])
            if group_hr_manager:
                pass
            # elif group_hr_officer:
            #     pass
            # elif group_recruitment_interviewer:
            # 	pass
            # elif group_recruitment_owner:
            # 	pass
            else:
                if len(employees) == 1:
                    if employees is not None:
                        if employees.user_id.id != request.uid:
                            raise UserError(
                                _("You are not allowed to access this employee. Please contact to your administrator."))

        check_method_name(method)
        return call_kw(request.env[model], method, args, kwargs)
