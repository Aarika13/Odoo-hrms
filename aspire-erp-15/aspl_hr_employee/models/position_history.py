import logging

from odoo import models, fields, api, _
from datetime import date, datetime
import time
from ..constant.constant import Constant
from ..common.validation import Validation
from odoo.exceptions import ValidationError, except_orm

_logger = logging.getLogger(__name__)


# Employee position history
class DesignationHistory(models.Model):
    _name = "designation.history"
    _description = "Employee designation history"
    _order = "effective_from desc"

    employee_id = fields.Many2one('hr.employee', 'Employee')  # , ondelete='restrict'
    category_type = fields.Char('Category Type', default='Designation', readonly=True)
    # category_ids = fields.Many2many('hr.employee.category', 'employee_designation_rel',
    # 'emp_id', 'category_id', 'Category', required=True)
    job_id = fields.Many2one('hr.job', 'Job Title', required=True)
    effective_from = fields.Date('Effective From', required=True)
    effective_to = fields.Date('Effective To')
    current_designation = fields.Boolean('Current Designation', default=True)

    # Constraints for effective_to validation
    @api.constrains('effective_from', 'effective_to')
    def _check_dates_constraints(self):
        if self.effective_from and self.effective_to:
            flag = Validation.check_date(self.effective_from, self.effective_to)
            if not flag:
                raise ValidationError(Constant.INVALID_DESIGNATION_DATE)
        return True

    '''
    def create(self, cr, uid, data, context):
        emp_id = data['employee_id']
        history_id = self.pool.get('designation.history').search(cr, uid, [('current_designation', '=', True),
                                                                           ['employee_id', '=', emp_id]],
                                                                 context=context)
        for record in self.browse(cr, uid, history_id, context=context):
            self.pool.get('designation.history').write(cr, uid, record.id,
                                                       {'effective_to': date.today(), 'current_designation': False})
        return super(DesignationHistory, self).create(cr, uid, data, context=context)
    '''
    # Need to uncomment
    # @api.model
    # def create(self, vals):
    #     if vals.get('employee_id'):
    #         history = self.env['designation.history'].search(
    #             [('current_designation', '=', True), ('employee_id', '=', vals.get('employee_id'))])
    #         for rec in history:
    #             rec.update({'effective_to': date.today(), 'current_designation': False})
    #     return super(DesignationHistory, self).create(vals)


class LocationHistory(models.Model):
    _name = "location.history"
    _description = "Employee location history"
    _order = "effective_from desc"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    category_type = fields.Char('Category Type', default='Location', readonly=True)
    location_street = fields.Char('Street', required=True)
    location_city = fields.Char('City', size=30, help='City max size is 30', required=True)
    location_pcode = fields.Char('Pin code', size=6, help='Pin Code max size is 6', required=True)
    location_id = fields.Many2one('res.country.state', 'State', required=True)
    location_county = fields.Many2one('res.country', 'Country', required=True)
    effective_from = fields.Date('Effective From', required=True)
    effective_to = fields.Date('Effective To')
    current_location = fields.Boolean('Current Location', default=True)

    # Constraints for effective_to validation
    @api.constrains('effective_from', 'effective_to')
    def _check_dates_constraints(self):
        if self.effective_from and self.effective_to:
            flag = Validation.check_date(self.effective_from, self.effective_to)
            if not flag:
                raise ValidationError(Constant.INVALID_LOCATION_DATE)
        return True

    '''
    def create(self, cr, uid, data, context):
        emp_id = data['employee_id']
        history_id = self.pool.get('location.history').search(cr, uid, [('current_location', '=', True),
                                                                        ('employee_id', '=', emp_id)], context=context)
        for record in self.browse(cr, uid, history_id, context=context):
            if record.id:
                self.pool.get('location.history').write(cr, uid, record.id,
                                                        {'effective_to': date.today(), 'current_location': False})
        return super(LocationHistory, self).create(cr, uid, data, context=context)
    '''
    # Need to uncomment
    # @api.model
    # def create(self, vals):
    #     if vals.get('employee_id'):
    #         location = self.env['location.history'].search(
    #             [('current_location', '=', True), ('employee_id', '=', vals.get('employee_id'))])
    #         for rec in location:
    #             rec.update({'effective_to': date.today(), 'current_location': False})
    #     return super(LocationHistory, self).create(vals)


class DepartmentHistory(models.Model):
    _name = "department.history"
    _description = "Employee Department history"
    _order = "effective_from desc"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    category_type = fields.Char('Category Type', default='Department', readonly=True)
    department_id = fields.Many2one('hr.department', 'Department', required=True)
    effective_from = fields.Date('Effective From', required=True)
    effective_to = fields.Date('Effective To')
    current_department = fields.Boolean('Current Department', default=True)

    # Constraints for effective_to validation
    @api.constrains('effective_from', 'effective_to')
    def _check_dates_constraints(self):
        if self.effective_from and self.effective_to:
            flag = Validation.check_date(self.effective_from, self.effective_to)
            if not flag:
                raise ValidationError(Constant.INVALID_DEPARTMENT_DATE)
        return True

    '''
    def create(self, cr, uid, data, context):
        emp_id = data['employee_id']
        history_id = self.pool.get('department.history').search(cr, uid, [('current_department', '=', True),
                                                                          ('employee_id', '=', emp_id)],
                                                                context=context)
        for record in self.browse(cr, uid, history_id, context=context):
            if record.id:
                self.pool.get('department.history').write(cr, uid, record.id,
                                                          {'effective_to': date.today(), 'current_department': False})
        return super(DepartmentHistory, self).create(cr, uid, data, context=context)
    '''
    # Need to uncomment after script
    # @api.model
    # def create(self, vals):
    #     if vals.get('employee_id'):
    #         department = self.env['department.history'].search(
    #             [('current_department', '=', True), ('employee_id', '=', vals.get('employee_id'))])
    #         for rec in department:
    #             rec.update({'effective_to': date.today(), 'current_department': False})
    #     return super(DepartmentHistory, self).create(vals)


class GradeHistory(models.Model):
    _name = "grade.history"
    _description = "Employee grade history"
    _order = "effective_from desc"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    category_type = fields.Char('Category Type', default='Grade', readonly=True)
    # grade_id = fields.Many2one('employee.grade.type', 'Grade', required=True)
    effective_from = fields.Date('Effective From', required=True)
    effective_to = fields.Date('Effective To')
    current_grade = fields.Boolean('Current Grade', default=True)

    # Constraints for effective_to validation
    @api.constrains('effective_from', 'effective_to')
    def _check_dates_constraints(self):
        if self.effective_from and self.effective_to:
            flag = Validation.check_date(self.effective_from, self.effective_to)
            if not flag:
                raise ValidationError(Constant.INVALID_GRADE_DATE)
        return True

    '''
    def create(self, cr, uid, data, context):
        emp_id = data['employee_id']
        history_id = self.pool.get('grade.history').search(cr, uid,
                                                           [('current_grade', '=', True), ('employee_id', '=', emp_id)],
                                                           context=context)
        for record in self.browse(cr, uid, history_id, context=context):
            if record.id:
                self.pool.get('grade.history').write(cr, uid, record.id,
                                                     {'effective_to': date.today(), 'current_grade': False})
        return super(GradeHistory, self).create(cr, uid, data, context=context)
    '''

    @api.model
    def create(self, vals):
        if vals.get('employee_id'):
            grade = self.env['grade.history'].search(
                [('current_grade', '=', True), ('employee_id', '=', vals.get('employee_id'))])
            for rec in grade:
                rec.update({'effective_to': date.today(), 'current_grade': False})
        return super(GradeHistory, self).create(vals)


class DivisionHistory(models.Model):
    _name = "division.history"
    _description = "Employee division history"
    _order = "effective_from desc"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    category_type = fields.Char('Category Type', default='Division', readonly=True)
    division_id = fields.Many2one('division.type', 'Division', required=True)
    effective_from = fields.Date('Effective From', required=True)
    effective_to = fields.Date('Effective To')
    current_division = fields.Boolean('Current Division', default=True)

    # Constraints for effective_to validation
    @api.constrains('effective_from', 'effective_to')
    def _check_dates_constraints(self):
        if self.effective_from and self.effective_to:
            flag = Validation.check_date(self.effective_from, self.effective_to)
            if not flag:
                raise ValidationError(Constant.INVALID_DIVISION_DATE)
        return True

    '''
    def create(self, cr, uid, data, context):
        emp_id = data['employee_id']
        history_id = self.pool.get('division.history').search(cr, uid, [('current_division', '=', True),
                                                                        ('employee_id', '=', emp_id)], context=context)
        for record in self.browse(cr, uid, history_id, context=context):
            if record.id:
                self.pool.get('division.history').write(cr, uid, record.id,
                                                        {'effective_to': date.today(), 'current_division': False})
        return super(DivisionHistory, self).create(cr, uid, data, context=context)
    '''

    @api.model
    def create(self, vals):
        if vals.get('employee_id'):
            division = self.env['division.history'].search(
                [('current_division', '=', True), ('employee_id', '=', vals.get('employee_id'))])
            for rec in division:
                rec.update({'effective_to': date.today(), 'current_division': False})
        return super(DivisionHistory, self).create(vals)


class DivisionType(models.Model):
    _name = "division.type"
    _description = "Division Type"

    name = fields.Char('Division', required=True)


class CostHistory(models.Model):
    _name = "cost.history"
    _description = "Employee cost history"
    _order = "effective_from desc"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    category_type = fields.Char('Category Type', default='Cost', readonly=True)
    cost_id = fields.Many2one('cost.type', 'Cost', required=True)
    effective_from = fields.Date('Effective From', required=True)
    effective_to = fields.Date('Effective To')
    current_cost = fields.Boolean('Current Division', default=True)

    # Constraints for effective_to validation
    @api.constrains('effective_from', 'effective_to')
    def _check_dates_constraints(self):
        if self.effective_from and self.effective_to:
            flag = Validation.check_date(self.effective_from, self.effective_to)
            if not flag:
                raise ValidationError(Constant.INVALID_COST_DATE)
        return True

    '''
    def create(self, cr, uid, data, context):
        emp_id = data['employee_id']
        history_id = self.pool.get('cost.history').search(cr, uid,
                                                          [('current_cost', '=', True), ('employee_id', '=', emp_id)],
                                                          context=context)
        for record in self.browse(cr, uid, history_id, context=context):
            if record.id:
                self.pool.get('cost.history').write(cr, uid, record.id,
                                                    {'effective_to': date.today(), 'current_cost': False})
        return super(CostHistory, self).create(cr, uid, data, context=context)
    '''

    @api.model
    def create(self, vals):
        if vals.get('employee_id'):
            cost = self.env['cost.history'].search(
                [('current_cost', '=', True), ('employee_id', '=', vals.get('employee_id'))])
            for rec in cost:
                rec.update({'effective_to': date.today(), 'current_cost': False})
        return super(CostHistory, self).create(vals)


class CostType(models.Model):
    _name = "cost.type"
    _description = "Cost Type"

    name = fields.Char('Cost Type', required=True)


class ReportingHistory(models.Model):
    _name = 'reporting.history'
    _description = 'reporting.history'
    _order = "effective_from desc"

    # def _domain_reporting_authority(self):
    #     reporting_authoritys = self.env.ref('base.group_hr_reporting_authority').users.ids
    #     return [('user_id.id', 'in', reporting_authoritys)]

    employee_id = fields.Many2one('hr.employee', 'Employee')
    category_type = fields.Char('Category Type', default='Reporting', readonly=True)
    parent_id = fields.Many2one('hr.employee', 'Reporting To', required=True)  # , domain=_domain_reporting_authority
    effective_from = fields.Date('Effective From', required=True)
    effective_to = fields.Date('Effective To')
    current_reporting = fields.Boolean('Current Reporting', default=True)

    @api.model
    def create(self,vals):
        emp_id = vals.get('employee_id')
        effective_from = vals.get('effective_from')
        parent_id = vals.get('parent_id')
        hr_employee_data = self.env['hr.employee'].browse(emp_id)
        parent_id_data = self.env['hr.employee'].browse(parent_id)
        position_history_data_list = hr_employee_data.position_reporting

        if position_history_data_list:
            effective_date_data = []
            for position_history in position_history_data_list:
                effective_date_data.append(position_history.effective_from)

            if effective_date_data:
                effective_date = max(effective_date_data)
                today = datetime.today()
                time = datetime.min.time()
                formatted_effective_from = datetime.strptime(effective_from, '%Y-%m-%d')
                formatted_effective_date = datetime.combine(effective_date,time)
                if formatted_effective_from > formatted_effective_date and formatted_effective_from <= today:
                    hr_employee_data.write({'parent_id':parent_id_data.id})
                    hr_employee_data.write({'coach_id':parent_id_data.id})

        else:
            hr_employee_data.write({'parent_id':parent_id_data.id})
            hr_employee_data.write({'coach_id':parent_id_data.id})
           
        return super(ReportingHistory, self).create(vals)

    
    
    
    # Constraints for effective_to validation
    @api.constrains('effective_from', 'effective_to')
    def _check_dates_constraints(self):
        if self.effective_from and self.effective_to:
            flag = Validation.check_date(self.effective_from, self.effective_to)
            if not flag:
                raise ValidationError(Constant.INVALID_REPORTING_DATE)
        return True

    '''
    def create(self, cr, uid, data, context):
        emp_id = data['employee_id']
        history_id = self.pool.get('reporting.history').search(cr, uid, [('current_reporting', '=', True),
                                                                         ('employee_id', '=', emp_id)], context=context)
        for record in self.browse(cr, uid, history_id, context=context):
            if record.id:
                self.pool.get('reporting.history').write(cr, uid, record.id,
                                                         {'effective_to': date.today(), 'current_reporting': False})
        return super(ReportingHistory, self).create(cr, uid, data, context=context)
    '''
    # Need to uncomment after script
    # @api.model
    # def create(self, vals):
    #     if vals.get('employee_id'):
    #         reporting = self.env['reporting.history'].search(
    #             [('current_reporting', '=', True), ('employee_id', '=', vals.get('employee_id'))])
    #         for rec in reporting:
    #             rec.update({'effective_to': date.today(), 'current_reporting': False})
    #     return super(ReportingHistory, self).create(vals)


# Employee position history
class CompanyHistory(models.Model):
    _name = "company.history"
    _description = "Employee company history"
    _order = "effective_from desc"

    employee_id = fields.Many2one('hr.employee', 'Employee')  # , ondelete='restrict'
    category_type = fields.Char('Category Type', default='company', readonly=True)
    # category_ids =  fields.Many2many('hr.employee.category',
    # 'employee_company_rel', 'emp_id', 'category_id', 'Category', required=True)
    employment_type = fields.Selection([
        ('permanent_employee', 'Permanent Employee'),
        ('consultant_aspire', 'Consultant Aspire'),
        ('trainee', 'Trainee'),
        ('temporary_employee', 'Temporary Employee'),
        ('client', 'Client'),
        ('consultant_other', 'Consultant Other')
    ], 'Employment Type', help="Select Employment Type")
    company_id = fields.Many2one('res.company', 'Company Name')
    company_employment_type = fields.Many2one('company.employment.type','Employment type',domain="[('company_id','=',company_id)]")

    effective_from = fields.Date('Effective From', required=True, default=datetime.today().date())
    effective_to = fields.Date('Effective To')     # , compute="_compute_effective_to", store=True
    current_company = fields.Boolean('Current company', default=True)
    employee_no = fields.Char("Employee No")

    def write(self, vals):
        if 'employee_id' in vals:
            employee_data = self.env['hr.employee'].search([('id','=',vals['employee_id'])])
            if employee_data:
                employee_data.write({'employee_no': self.employee_no, 'employee_no_type': self.company_employment_type.company_employment_type,
                                     'company_id': self.company_id.id})
        return super(CompanyHistory, self).write(vals)
            
    
    
    # def _compute_effective_to(self):
    #     record = [i for i in self]
    #     if len(record) > 1:
    #         record[1].effective_to = record[0].effective_from
    #         record[0].effective_to = False
    #     else:
    #         self.effective_to = False

    # Constraints for effective_to validation
    @api.constrains('effective_from', 'effective_to')
    def _check_dates_constraints(self):
        for rec in self:
            if rec.effective_from and rec.effective_to and (rec.effective_to != rec.effective_from):
                flag = Validation.check_date(rec.effective_from, rec.effective_to)
                if not flag:
                    raise ValidationError(Constant.INVALID_COMPANY_DATE)
        return True

    # @api.onchange('company_id', 'employment_type')
    # def on_change_company_transfer(self):
    #     self._compute_employee_no()
        # all_rec = [i for i in self.employee_id.position_company]
        # previous_dates = [i.effective_from for i in self.employee_id.position_company]
        # for record in self:
        #     print("------------------------------------------------------------------------")
        #     print("\nrecord.employee_id\n", record.employee_id, record.employee_id.id) # NewId_4
        #     emp_id = str(record.employee_id.id).split('_')[-1]
        #     print(emp_id, type(emp_id), emp_id.isnumeric())
            # if emp_id.isnumeric():
            #     len_app = len(record.employee_id.position_company)
            #     emp_obj = self.env['hr.employee'].search([('id', '=', emp_id)])
            #         emp_obj.write({
            #             'company_id': record.company_id.id,
            #             'employee_no_type': record.employment_type,
            #             'employee_no': record.employee_no,
            #         })
            #     else:
            #         emp_obj.write({
            #             'company_id': record.company_id.id,
            #             'employee_no_type': record.employment_type,
            #             'employee_no': record.employee_no,
            #         })
            # else:
            #     raise ValidationError(_("Please save employee before adding company history."))

    def next_by_code(self, sequence_code, sequence_date=None):
        self.env['ir.sequence'].check_access_rights('read')
        seq_ids = self.env['ir.sequence'].search([('code', '=', sequence_code)])
        seq_id = seq_ids[0]
        return seq_id._next(sequence_date=sequence_date)
    
    def _get_previous_by_code(self,sequence):
        employee_next_no = sequence.get_next_char(sequence.number_next_actual)
        next_number_actual_count = int(sequence.number_next_actual) - 1
        employee_no = int(employee_next_no) - 2
        check_employee_no = self.env['company.history'].search([('employee_no','ilike',str(employee_no))])
        if check_employee_no:
            raise ValidationError(_("You are not able to perform Previous step."))
        else:
            sequence.write({'number_next_actual':next_number_actual_count})
            return employee_no


    def generate_sequence_employee(self):
        sequence = self.env['ir.sequence'].search([('name', '=',self.company_employment_type.company_employment_type),('company_id','=',self.company_id.id)])
        if sequence:
            sequence_code = sequence.code
            self.employee_no = self.next_by_code(sequence_code)
        else:
            raise ValidationError(_("Make sure sequence created for this combination."))
        return self


    def get_previous_sequence_employee(self):
        sequence = self.env['ir.sequence'].search([('name', '=',self.company_employment_type.company_employment_type),('company_id','=',self.company_id.id)])
        self.employee_no = self._get_previous_by_code(sequence)
        return self  
    


    '''
    def create(self, cr, uid, data, context):
        emp_id = data['employee_id']
        history_id = self.pool.get('company.history').search(cr, uid, [('current_company', '=', True),
                                                                       ['employee_id', '=', emp_id]], context=context)
        for record in self.browse(cr, uid, history_id, context=context):
            self.pool.get('company.history').write(cr, uid, record.id,
                                                   {'effective_to': datetime.date.today(), 'current_company': False})
        return super(CompanyHistory, self).create(cr, uid, data, context=context)
    '''
    # Need to uncomment after script
    # @api.model
    # def create(self, vals):
    #     if vals.get('employee_id'):
    #         company = self.env['company.history'].search(
    #             [('current_company', '=', True), ('employee_id', '=', vals.get('employee_id'))])
    #         for rec in company:
    #             rec.update({'effective_to': date.today(), 'current_company': False})
    #     return super(CompanyHistory, self).create(vals)
