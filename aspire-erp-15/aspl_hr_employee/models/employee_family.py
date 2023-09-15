import logging
from ..constant.constant import Constant
from ..common.validation import Validation
from odoo.exceptions import ValidationError, except_orm
from odoo import models, fields, api, _

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
    ('other', 'Other'),
]


# Employee family information
class FamilyMember(models.Model):
    _name = 'family.member'
    _description = 'Family Member'

    @api.onchange('copy_address_from')
    def on_change_opy_address_from(self):
        for record in self:
            if record.copy_address_from == "present_address":
                record.home_street = record.employee_id.pre_street
                record.home_city = record.employee_id.pre_city
                record.home_landmark = record.employee_id.pre_landmark
                record.home_pcode = record.employee_id.pre_pcode
                record.home_state = record.employee_id.pre_state
                record.home_county = record.employee_id.pre_county
            elif record.copy_address_from == "permanent_address":
                record.home_street = record.employee_id.per_street
                record.home_city = record.employee_id.per_city
                record.home_landmark = record.employee_id.per_landmark
                record.home_pcode = record.employee_id.per_pcode
                record.home_state = record.employee_id.per_state
                record.home_county = record.employee_id.per_county

    @api.onchange('check_per_address')
    def on_change_check_per_address(self):
        for record in self:
            record.home_street = None
            record.home_city = None
            record.home_landmark = None
            record.home_pcode = None
            record.home_state = None
            record.home_county = None
            record.copy_address_from = None

    employee_id = fields.Many2one('hr.employee', 'Employee')
    name = fields.Char('Name', size=60)  # , required=True
    birth_date = fields.Date('DOB')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender')
    blood_group = fields.Selection(
        [('o+', 'O+'), ('o-', 'O-'), ('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('b-', 'B-'), ('ab+', 'AB+'),
         ('ab-', 'AB-')], 'Blood Group')
    relation = fields.Selection(RELATION, 'Relation')  # , required=True
    profession = fields.Char('Profession')
    nationality = fields.Many2one('res.country', 'Nationality', default=lambda self: self.env.company.country_id)
    remarks = fields.Text('Remarks')
    check_per_address = fields.Boolean('Address Same As employee')
    copy_address_from = fields.Selection(
        [('present_address', 'Present Address'), ('permanent_address', 'Permanent Address')], 'Copy Address From')
    home_street = fields.Char('Street')
    home_landmark = fields.Char('Landmark')
    home_city = fields.Char('City', size=30)
    home_pcode = fields.Char('Pin Code', size=6, help="Max size is 6")  # , required=True
    home_state = fields.Many2one('res.country.state', 'State')  # , required=True
    home_county = fields.Many2one('res.country', 'Country')  # , required=True
    home_phone = fields.Char('Mobile Phone')

    # Constraints for validation
    @api.constrains('name', 'home_pcode', 'home_phone')
    def _check_constraints(self):
        for rec in self:
            if rec.name:
                flag = Validation.check_names(rec.name)
                if not flag:
                    raise ValidationError(Constant.INVALID_MEMBER_NAME)
            if rec.home_pcode:
                flag = Validation.check_digit(rec.home_pcode)
                if not flag:
                    raise ValidationError(Constant.INVALID_MEMBER_PINCODE)
            if rec.home_phone:
                flag = Validation.check_phone(rec.home_phone)
                if not flag:
                    raise ValidationError(Constant.INVALID_MEMBER_PHONE)
            return True


class MemberRelation(models.Model):
    _name = 'member.relation'
    _description = 'Member Relation'
    _rec_name = 'rel_name'

    rel_name = fields.Char('Relation', size=30)  # , required=True

    # Constraints for validation
    @api.constrains('rel_name')
    def _check_constraints(self):
        for rec in self:
            if rec.rel_name:
                flag = Validation.check_names(rec.rel_name)
                if not flag:
                    raise ValidationError(Constant.INVALID_RELATION_NAME)
