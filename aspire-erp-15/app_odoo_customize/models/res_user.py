
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)
class FamilyMemberInherit(models.Model):
    _inherit = 'family.member'
    
    emp_user_id = fields.Many2one('res.users', 'Employee User')


class ResUserInherit(models.Model):
    _inherit = 'res.users'

    blood_group = fields.Selection(related='employee_id.blood_group', readonly=False,string='Blood Group',related_sudo=False)
    religion = fields.Char(related='employee_id.religion',string='Religion',readonly=False)
    # international_employee = fields.Boolean(related='employee_id.international_employee', string='International Employee',readonly=False)
    physically_challenged = fields.Boolean('Physically Challenged',related='employee_id.physically_challenged',readonly=False)
    isPresentAddSameAsPermanent = fields.Boolean(related='employee_id.isPresentAddSameAsPermanent',string='Same as Permanent Address',readonly=False)
    
    marriage_date = fields.Date(related='employee_id.marriage_date',string='Marriage Date',readonly=False)
    pre_street = fields.Char('Present Street',related='employee_id.pre_street',readonly=False)
    pre_landmark = fields.Char('Present Landmark',related='employee_id.pre_landmark',readonly=False)
    pre_city = fields.Char('Present City',related='employee_id.pre_city', size=30, help='City max size is 30',readonly=False)
    pre_pcode = fields.Char('Present Pin code', related='employee_id.pre_pcode',size=6, help='Pincode max size is 6',readonly=False)
    pre_state = fields.Many2one(related='employee_id.pre_state',readonly=False)
    pre_county = fields.Many2one(related='employee_id.pre_county',readonly=False)
    from_employee_test = fields.Char("Test Field For Employee")

    # Employee family detail
    family_member_id = fields.One2many(related='employee_id.family_member_id',readonly=False)

    @api.onchange('isPresentAddSameAsPermanent')
    def on_change_is_Present_Add_Same_As_Permanent(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_street = record.private_street
                record.pre_landmark = record.private_street2
                record.pre_city = record.private_city
                record.pre_pcode = record.private_zip
                record.pre_state = record.private_state_id
                record.pre_county = record.private_country_id
            else:
                record.pre_street = None
                record.pre_landmark = None
                record.pre_city = None
                record.pre_pcode = None
                record.pre_state = None
                record.pre_county = None
                
    @api.onchange('private_street')
    def on_change_pre_street(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_street = record.private_street

    @api.onchange('private_street2')
    def on_change_per_landmark(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_landmark = record.private_street2

    @api.onchange('private_city')
    def on_change_per_city(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_city = record.private_city

    @api.onchange('private_zip')
    def on_change_per_pcode(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_pcode = record.private_zip

    @api.onchange('private_state_id')
    def on_change_per_state(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_state = record.private_state_id

    @api.onchange('private_country_id')
    def on_change_per_county(self):
        for record in self:
            if record.isPresentAddSameAsPermanent:
                record.pre_county = record.private_country_id

    def write(self,vals):
        if 'from_employee_test' in vals:
            pass
        else:
            employee_data = {}
            if 'private_street' in  vals:
                employee_data['per_street'] = vals['private_street']
            
            if 'private_street2' in vals:
                employee_data['per_landmark'] = vals['private_street2']

            if 'private_city' in vals:
                employee_data['per_city'] = vals['private_city']

            if 'private_zip' in vals:
                employee_data['per_pcode'] = vals['private_zip']

            if 'private_country_id' in vals:
                employee_data['per_county'] = vals['private_country_id']

            if 'private_state_id' in vals:
                employee_data['per_state'] = vals['private_state_id']

            if 'employee_phone' in vals:
                employee_data['per_phone1'] = vals['employee_phone']

            if 'private_email' in vals:
                employee_data['personal_email'] = vals['private_email']

            if 'employee_country_id' in vals:
                employee_data['country_id'] = vals['employee_country_id']

            if employee_data:
                employee_data['from_user_test'] = self.id
                self.env['hr.employee'].sudo().search([('user_id', '=', self.id)]).write(employee_data)
      
            result = super(ResUserInherit, self).write(vals)
            return result
    


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    from_user_test = fields.Char("Test Field For user")


    def write(self,vals):
        
        if 'from_user_test' in vals:
            pass
        else:
            user_data = {}
            if 'per_street' in  vals:
                user_data['private_street'] = vals['per_street']
            
            if 'per_landmark' in vals:
                user_data['private_street2'] = vals['per_landmark']

            if 'per_city' in vals:
                user_data['private_city'] = vals['per_city']

            if 'per_pcode' in vals:
                user_data['private_zip'] = vals['per_pcode']

            if 'per_county' in vals:
                user_data['private_country_id'] = vals['per_county']

            if 'per_state' in vals:
                user_data['private_state_id'] = vals['per_state']

            if 'per_phone1' in vals:
                user_data['employee_phone'] = vals['per_phone1']

            if 'personal_email' in vals:
                user_data['private_email'] = vals['personal_email']

            if 'country_id' in vals:
                user_data['employee_country_id'] = vals['country_id']

            if user_data:
                user_data['from_employee_test'] = self.id
                self.env['res.users'].sudo().search([('id', '=', self.user_id.id)]).write(user_data)
        
            result = super(HrEmployeeInherit, self).write(vals)
            return result
