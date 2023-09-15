import logging
from odoo import models, fields, api, _
from dateutil import parser
from ..constant.constant import Constant
from ..common.validation import Validation
from odoo.exceptions import ValidationError, except_orm

_logger = logging.getLogger(__name__)


# Employee Passport & Visa information
class EmployeePassport(models.Model):
    _name = 'employee.passport'
    _description = 'Employee Passport'

    # Add employee passport & visa information
    employee_id = fields.Many2one('hr.employee', 'Employee')
    name = fields.Char('First Name')  # , required=True
    sur_name = fields.Char('Last Name')
    middle_name = fields.Char('Middle Name')
    pass_add1 = fields.Char('Passport Address1')
    pass_add2 = fields.Char('Passport Address2')
    pass_add3 = fields.Char('Passport Address3')
    currently_with = fields.Char('Currently With')
    county = fields.Many2one('res.country', 'Country')  # , required=True
    passport_num = fields.Char('Passport No', size=8)  # , required=True
    passport_type = fields.Many2one('passport.type', 'Passport Type')
    issue_place = fields.Char('Issue Place', size=50)
    issue_city = fields.Char('Issue City', size=50)
    issue_date = fields.Date('Issue Date')  # , required=True
    valid_till = fields.Date('Valid Till')  # , required=True

    # Constraints for name validation
    @api.constrains('name', 'sur_name', 'middle_name', 'currently_with', 'passport_num')
    def _check_name_constraints(self):
        if self.name:
            flag = Validation.check_names(self.name)
            if not flag:
                raise ValidationError(Constant.INVALID_PASSPORT_NAME)
        if self.sur_name:
            flag = Validation.check_names(self.sur_name)
            if not flag:
                raise ValidationError(Constant.INVALID_PASSPORT_SUR_NAME)
        if self.middle_name:
            flag = Validation.check_names(self.middle_name)
            if not flag:
                raise ValidationError(Constant.INVALID_MIDDLE_NAME)
        if self.currently_with:
            flag = Validation.check_names(self.currently_with)
            if not flag:
                raise ValidationError(Constant.INVALID_CURRENTLY_WITH)
        if self.passport_num:
            flag = Validation.check_passport_num(self.passport_num)
            if not flag:
                raise ValidationError(Constant.INVALID_PASSPORT_NUMBER)
        return True

    # def onchange_dates(self, cr, uid, ids, issue_date, valid_till):
    #     res = {'value': {}}
    #     if issue_date == False:
    #         return {'value': {'valid_till': False}}
    #     if valid_till == False:
    #         return {'value': {'valid_till': False}}
    #     if parser.parse(issue_date) >= parser.parse(valid_till):
    #         res['value']['valid_till'] = ''
    #     return res


class PassportType(models.Model):
    _name = 'passport.type'
    _description = 'Passport Type'
    _rec_name = 'passport_type'

    passport_type = fields.Char('Passport Type')  # , required=True


class EmployeeVisa(models.Model):
    _name = 'employee.visa'
    _description = 'Employee Visa'

    # Add employee passport & visa information
    employee_id = fields.Many2one('hr.employee', 'Employee')
    name = fields.Char('Name')  # , required=True
    county = fields.Many2one('res.country', 'Country')  # , required=True
    visa_type = fields.Many2one('visa.type', 'Visa Type')  # , required=True
    visa_no = fields.Char('Visa No', size=30)  # , required=True
    issue_date = fields.Date('Issue Date')  # , required=True
    valid_till = fields.Date('Valid Till')  # , required=True

    # Constraints for name validation
    @api.constrains('name')
    def _check_name_constraints(self):
        if self.name:
            flag = Validation.check_names(self.name)
            if not flag:
                raise ValidationError(Constant.INVALID_VISA_NAME)
        return True

    # def onchange_dates(self, cr, uid, ids, issue_date, valid_till):
    #     res = {'value': {}}
    #     if issue_date == False:
    #         return {'value': {'valid_till': False}}
    #     if valid_till == False:
    #         return {'value': {'valid_till': False}}
    #     if parser.parse(issue_date) >= parser.parse(valid_till):
    #         res['value']['valid_till'] = ''
    #     return res


class VisaType(models.Model):
    _name = 'visa.type'
    _rec_name = 'visa_type'
    _description = 'Visa Type'

    visa_type = fields.Char('Visa Type')  # , required=True
