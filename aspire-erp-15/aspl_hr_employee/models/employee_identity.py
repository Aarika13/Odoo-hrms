import logging
from odoo import models, fields, api, _
from ..constant.constant import Constant
import re
import odoo.exceptions
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

IDENTITY = [
    ('aadhaar', 'AADHAAR CARD'),
    ('election_card', 'ELECTION CARD'),
    ('passport', 'PASSPORT'),
    ('account_number', 'PERMANENT A/C No'),
    ('bank_account', 'Bank A/C No'),
    ('driving_license', 'Driving License'),
    ('passport_size_photo', 'Passport Photo'),
]


# Employee Identity Information
class EmployeeIdentity(models.Model):
    _name = 'employee.identity'
    _description = 'Employee Identity'

    @api.onchange('aadhaar_no')
    def on_change_aadhaar_no(self):
        for record in self:
            if record.aadhaar_no:
                record.complete_name = 'Aadhaar Card [' + record.aadhaar_no + ' ] '

    @api.onchange('license_number')
    def on_change_license_number(self):
        for record in self:
            if record.license_number:
                record.complete_name = 'Driving License Number [' + record.license_number + ' ] '

    @api.onchange('bank_acc')
    def on_change_bank_acc(self):
        for record in self:
            if record.bank_acc:
                record.complete_name = 'Bank Account [' + record.bank_acc + ' ] '

    @api.onchange('pan_no')
    def on_change_pan_no(self):
        for record in self:
            if record.pan_no:
                record.complete_name = 'Pan Number[' + record.pan_no + ' ] '

    @api.onchange('passport_no')
    def on_change_passport_no(self):
        for record in self:
            if record.passport_no:
                record.complete_name = 'Passport [' + record.passport_no + ' ] '

    @api.onchange('ec_no')
    def on_change_ec_no(self):
        for record in self:
            if record.ec_no:
                record.complete_name = 'Election Card [' + record.ec_no + ' ] '

    employee_id = fields.Many2one('hr.employee', 'Employee')
    employee_identity = fields.Selection(IDENTITY, 'Document Type', required=True)
    complete_name = fields.Char(compute='_dept_name_get_fnc', type="char", string='Name')
    aadhaar_no = fields.Char('Aadhaar Number', size=30)
    aadhaar_name = fields.Char('Name in Aadhaar', size=60)
    aadhaar_enrolno = fields.Char('Aadhaar Enrolment No', size=50)
    ec_no = fields.Char('EC Number', size=30)
    ec_name = fields.Char('Name in EC', size=60)
    passport_no = fields.Char('Passport Number', size=30)
    passport_name = fields.Char('Name in Passport', size=60)
    expire_date = fields.Date('Expiry Date')
    pan_no = fields.Char('PAN', size=10)
    pan_name = fields.Char('Name in PAN', size=60)
    bank_acc = fields.Char('Bank A/C No', size=30)
    bank_ifsc = fields.Char('IFSC', size=20)
    bank_acc_name = fields.Char("Name in Bank A/c", size=60)
    document_verified = fields.Boolean('Document Verified')
    license_name = fields.Char('License Name')
    license_number = fields.Char('License Number')
    document = fields.Binary('Document', required=True)
    document_name = fields.Char('Attachment Name', required=True)

    def _dept_name_get_fnc(self):
        for record in self:
            name = record['employee_identity']
            if name == 'aadhaar':
                record.complete_name = 'Aadhaar Card [ ' + record['aadhaar_no'] + ' ]'
            if name == 'election_card':
                record.complete_name = 'Election Card [ ' + record['ec_no'] + ' ]'
            if name == 'passport':
                record.complete_name = 'Passport [ ' + record['passport_no'] + ' ]'
            if name == 'account_number':
                record.complete_name = 'Pan Number [ ' + record['pan_no'] + ' ]'
            if name == 'bank_account':
                record.complete_name = 'Bank Account [ ' + record['bank_acc'] + ' ]'
            if name == 'driving_license':
                record.complete_name = 'Driving License Number[ ' + record['license_number'] + ' ]'
            if name == 'passport_size_photo':
                record.complete_name = 'Passport Size Photo'
        return True

    def name_get(self):
        if not self.ids:
            return []
        res = []
        for record in self:
            name = record['employee_identity']
            if name == 'aadhaar':
                name = 'Aadhaar Card [' + record['aadhaar_no'] + ' ] '
            if name == 'election_card':
                name = 'Election Card [' + record['ec_no'] + ' ] '
            if name == 'passport':
                name = 'Passport [' + record['passport_no'] + ' ] '
            if name == 'account_number':
                name = 'Pan Number [' + record['pan_no'] + ' ] '
            if name == 'bank_account':
                name = 'Bank Account [' + record['bank_acc'] + ' ] '
            if name == 'driving_license':
                name = 'Driving License Number[' + record['license_number'] + ' ] '
            if name == 'passport_size_photo':
                name = 'Passport Size Photo'
            res.append((record['id'], name))
        return res

    # Need to uncomment after script
    def create(self, data):
        value = None
        identity = ''
        for val in data:
            identity += val['employee_identity']
            break
        if identity == 'aadhaar':
            value = aadhaar_validation(data[0])
        if identity == 'election_card':
            value = election_validation(data)
        if identity == 'passport':
            value = passport_validation(data)
        if identity == 'account_number':
            value = pan_validation(data)
        if identity == 'bank_account':
            value = bank_validation(data)
        if identity == 'driving_license':
            value = license_validation(data)
        if identity == 'passport_size_photo':
            value = passport_photo_validation(data)

        if value:
            return super(EmployeeIdentity, self).create(data)
        else:
            raise odoo.exceptions.Warning(" %s " % value)

    def write(self, val):
        value = None
        for data in self:
            identity = data['employee_identity']
            if identity == 'aadhaar':
                value = aadhaar_validation(val)
            if identity == 'election_card':
                value = election_validation(val)
            # if identity == 'passport':
            #     value = passport_validation(val)
            if identity == 'account_number':
                value = pan_validation(val)
            if identity == 'bank_account':
                value = bank_validation(val)
            if identity == 'driving_license':
                value = license_validation(data)
            if identity == 'passport_size_photo':
                value = passport_photo_validation(data)
            if value:
                return super(EmployeeIdentity, self).write(val)
            else:
                raise odoo.exceptions.Warning(" %s " % value)


def aadhaar_validation(data):
    flag = 0
    if 'aadhaar_no' in data:
        aadhaar_num = str(data['aadhaar_no']) if type(data['aadhaar_no']) != str else data['aadhaar_no']

        if not aadhaar_num: 
            raise ValidationError(_(Constant.REQUIRED_AADHAAR_NO)) 
        elif not aadhaar_num.isdigit(): 
            raise ValidationError(_(Constant.INVALID_AADHAAR_NO)) 
        elif len(aadhaar_num) != 12: 
            raise ValidationError(_('Enter only 12 digits in "Aadhaar Number"'))
        flag = 1
    
    if 'aadhaar_name' in data: 
        aadhaar_name = data['aadhaar_name'] 
        if not aadhaar_name: 
            raise ValidationError(_(Constant.REQUIRED_AADHAAR_NAME)) 
        elif re.match("^[a-zA-Z\s]+$", aadhaar_name) == None: 
            raise ValidationError(_(Constant.INVALID_AADHAAR_NAME))
        flag = 1
    if flag == 1:    
        return True


def election_validation(data):
    if 'ec_no' in data:
        ec_no = data['ec_no']
        if not ec_no:
            return (Constant.REQUIRED_EC_NO)
    if 'ec_name' in data:
        ec_name = data['ec_name']
        if not ec_name:
            return (Constant.REQUIRED_EC_NAME)
        elif re.match("^[a-zA-Z\s]+$", ec_name) == None:
            return (Constant.INVALID_EC_NAME)
    return True


# Need to uncomment after script
def passport_validation(data):
    if 'passport_no' in data:
        passprt_no = data['passport_no']
        if not passprt_no:
            return (Constant.REQUIRED_PASSPORT_NO)
    if 'passport_name' in data:
        passport_name = data['passport_name']
        if not passport_name:
            return (Constant.REQUIRED_PASSPORT_NAME)
        elif re.match("^[a-zA-Z\s]+$", passport_name) == None:
            return (Constant.INVALID_PASSPORT_NAME)
    if 'expire_date' in data:
        expire_date = data['expire_date']
        if not expire_date:
            return (Constant.REQUIRED_EXPIRE_DATE)
    return True


def pan_validation(data):
    if 'pan_no' in data:
        pan_no = data['pan_no']
        if not pan_no:
            raise Exception(_('Enter "PAN Number" must be required'))

    if 'pan_name' in data:
        pan_name = data['pan_name']
        if not pan_name:
            return (Constant.REQUIRED_PAN_NAME)
        elif re.match("^[a-zA-Z\s]+$", pan_name) == None:
            return ('Enter only alphabets in "PAN Name"')
    return True


def bank_validation(data):
    if 'bank_acc' in data:
        bank_acc = data['bank_acc']
        if not bank_acc:
            return (Constant.REQUIRED_BANK_ACC_NO)
        elif not bank_acc.isdigit():
            return (Constant.INVALID_BANK_ACC_NO)

    if 'bank_ifsc' in data:
        bank_ifsc = data['bank_ifsc']
        if not bank_ifsc:
            return (Constant.REQUIRED_IFSC_CODE)

    if 'bank_acc_name' in data:
        bank_acc_name = data['bank_acc_name']
        if not bank_acc_name:
            return Constant.REQUIRED_BANK_NAME
        elif re.match("^[a-zA-Z\s]+$", bank_acc_name) is None:
            return Constant.INVALID_BANK_NAME
    return True


def license_validation(data):
    if 'license_number' in data:
        license_number = data['license_number']
        if not license_number:
            return Constant.REQUIRED_LICENSE_NO

    if 'license_name' in data:
        license_name = data['license_name']
        if not license_name:
            return Constant.REQUIRED_LICENSE_NAME
        elif re.match("^[a-zA-Z\s]+$", license_name) is None:
            return Constant.INVALID_LICENSE_NAME
    return True


def passport_photo_validation(data):
    # print("\n\npassport_photo_validation called\n\n")
    # print(data)
    # if 'document' in data:
    #     doc_name = data['document'].split('.')
    #     print(doc_name)
    #     if doc_name[-1].lower() not in ('jpg', 'jpeg'):
    #         return Constant.INVALID_FILE_TYPE
    return True
