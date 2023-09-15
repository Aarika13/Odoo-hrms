import logging
from odoo import models, fields, api, _
from dateutil import parser
from odoo.exceptions import ValidationError, except_orm
from ..constant.constant import Constant
from ..common.validation import Validation

_logger = logging.getLogger(__name__)


class EmployeeEducation(models.Model):
    _name = 'employee.education'
    _description = 'Employee Education'
    _rec_name = 'degree'

    # def unlink(self, cr, uid, ids, context=None):
    # 	for line in self.browse(cr, uid, ids):
    # 		if line.qualification == 'graduate':
    # 			raise osv.except_osv('error!', 'Not allowed to delete record with qualification "Graduate"')
    # 	return super(employee_education, self).unlink(cr, uid, ids)

    def unlink(self):
        for line in self:
            if line.qualification == 'graduate':
                raise ValidationError(_('error!', 'Not allowed to delete record with qualification "Graduate"'))
        return super(EmployeeEducation, self).unlink()

    employee_id = fields.Many2one('hr.employee', 'Employee')
    degree = fields.Many2one('employee.degree', 'Degree')  # , required=True
    field_id = fields.Many2one('employee.field', 'Field')
    university = fields.Char('University')
    institute = fields.Char('Institute')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    qualification = fields.Selection(related='degree.qualification', string='Qualification')
    percentage = fields.Float('Percentage', digits=(2, 2))

    '''
    Domain update deprecated new version of Odoo
    def onchange_field(self, cr, uid, ids, degree, context=None):
        field_obj = self.pool.get('employee.field')
        field_data = field_obj.search(cr, uid, [('degree_id', '=', degree)], context=context)
        qualificationDataObj = self.pool.get('employee.degree').browse(cr, uid, degree, context=context)
        res = {'domain': {'field_id': [('id', 'in', field_data)]},
               'vals': {'qualification': qualificationDataObj.qualification}}
        return res

    def onchange_dates(self, cr, uid, ids, start_date, end_date):
        res = {'value': {}}
        if start_date == False:
            return {'value': {'end_date': False}}
        if end_date == False:
            return {'value': {'end_date': False}}
        if parser.parse(start_date) >= parser.parse(end_date):
            res['value']['end_date'] = ''
        return res
    '''

    # Constraints for confirm_date validation
    @api.constrains('end_date')
    def _check_dates_constraints(self):
        if self.end_date:
            flag = Validation.check_confirm_date(self.start_date, self.end_date)
            if not flag:
                raise ValidationError(Constant.INVALID_POSITATION_DATE)
        return True


class EmployeeDegree(models.Model):
    _name = 'employee.degree'
    _description = "Employee Degree"
    _rec_name = 'degree_name'

    degree_name = fields.Char('Degree Name')  # , required=True
    qualification = fields.Selection(
        [('undergraduate', 'Under Graduate'),
         ('graduate', 'Graduate'),
         ('postgraduate', 'Post Graduate')],
        'Qualification')


class EmployeeField(models.Model):
    _name = 'employee.field'
    _description = "Employee field"
    _rec_name = 'field_name'

    degree_id = fields.Many2one('employee.degree', 'Degree')  # , required=True
    field_name = fields.Char('Field Name')  # , required=True
