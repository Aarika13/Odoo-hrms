import logging
from ..constant.constant import Constant
from ..common.validation import Validation
from odoo.exceptions import ValidationError, except_orm
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class HrBankDetail(models.Model):
    _name = "hr.bank.detail"
    _description = "Bank Detail"
    _rec_name = 'bank_name'

    bank_name = fields.Char('Bank Name', size=100, required=True)
    ifsc_code = fields.Char('IFSC Code', size=20, help="Max size 20", required=True)
    bank_street = fields.Char('Street')
    bank_landmark = fields.Char('Landmark')
    bank_pcode = fields.Char('Pin code', size=6, help='Pincode max size is 6')
    bank_city = fields.Char('City', size=30, help='City max size is 30')
    bank_state = fields.Many2one('res.country.state', 'State')
    bank_county = fields.Many2one('res.country', 'Country')
    phone = fields.Char('Phone')

    @api.constrains('bank_pcode', 'phone')
    def _check_constraints(self):
        if self.bank_pcode:
            flag = Validation.check_digit(self.bank_pcode)
            if not flag:
                raise ValidationError(Constant.INVALID_PCODE)
        if self.phone:
            flag = Validation.check_phone(self.phone)
            if not flag:
                raise ValidationError(Constant.INVALID_MOBILE_PHONE)
        return True


class HrBankAccountType(models.Model):
    _name = "hr.bank.account.type"
    _description = "Account Type"
    _rec_name = 'account_type'

    account_type = fields.Char('Account Type', size=30, required=True)
