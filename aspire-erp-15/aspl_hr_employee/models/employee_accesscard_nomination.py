from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from ..constant.constant import Constant
from ..common.validation import Validation
from dateutil import parser

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


class AccessCardDetail(models.Model):
    _name = 'access.card.detail'
    _description = "Access Card Detail"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    card_no = fields.Char('Access Card Number')  # , required=True
    start_date = fields.Date('From Date')  # , required=True
    end_date = fields.Date('To Date')

    '''
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


class NominationType(models.Model):
    _name = 'nomination.type'
    _description = "Nomination Type"

    name = fields.Char('Nomination Type', required=True)


class NominationDetail(models.Model):
    _name = 'nomination.detail'
    _description = "Nomination Type"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    employee = fields.Many2one('hr.employee', 'Employee', required=True)
    nomination_id = fields.Many2one('nomination.type', 'Nomination For', required=True)
    family_member = fields.Many2one('family.member', 'Family Member', required=True)
    mental = fields.Boolean('Mental Illness')
    minor = fields.Boolean('Minor')
    guardian_name = fields.Char('Guardian Name')
    guardian_relation = fields.Selection(RELATION, 'Guardian Relation')
    same_address = fields.Boolean('Guardian Address Same As Nominee')
    home_street = fields.Char('Street')
    home_landmark = fields.Char('Landmark')
    home_city = fields.Char('City', size=30)
    home_pcode = fields.Char('Pin code', size=6, help="Max size is 6")
    home_state = fields.Many2one('res.country.state', 'State')
    home_county = fields.Many2one('res.country', 'Country')
    home_phone = fields.Char('Phone')
    home_mobile = fields.Char('Mobile')
    email = fields.Char('Email')

    # Constraints for validation
    @api.constrains('home_phone', 'home_mobile', 'email')
    def _check_constraints(self):
        if self.home_phone:
            flag = Validation.check_phone(self.home_phone)
            if not flag:
                raise ValidationError(Constant.INVALID_NOMINATION_PHONE)
        if self.home_mobile:
            flag = Validation.check_phone(self.home_mobile)
            if not flag:
                raise ValidationError(Constant.INVALID_NOMINATION_MOBILE)
        if self.email:
            flag = Validation.check_email(self.email)
            if not flag:
                raise ValidationError(Constant.INVALID_NOMINATION_EMAIL)
        return True

    '''
    domain return in onchange is not support in new version of Odoo
    def onchange_member(self, cr, uid, ids, employee_id, context):
        if employee_id:
            val = {}
            family_obj = self.env['family.member'].search([(('employee_id', '=', employee_id))])
            family_obj = self.pool.get('family.member')
            family_data = family_obj.search(cr, uid, [('employee_id', '=', employee_id)], context=context)
            res = {'domain': {'family_member': [('id', 'in', family_data)]}}
            return res
    '''
