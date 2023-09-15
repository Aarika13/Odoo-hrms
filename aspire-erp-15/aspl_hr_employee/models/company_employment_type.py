import logging

from odoo import models, fields, api, _
from datetime import date, datetime
import time
from ..constant.constant import Constant
from ..common.validation import Validation
from odoo.exceptions import ValidationError, except_orm

_logger = logging.getLogger(__name__)


class CompanyEmploymentType(models.Model):
    _name = "company.employment.type"
    _description = "Company Employment Type"

    name = fields.Char(string="Employment Name",required = True)
    company_id = fields.Many2one('res.company', 'Company Name',required = True)

    company_employment_type = fields.Char(string="Employment Type")

    prefix_sequence = fields.Integer("Prefix",required = True,help="Create Prefix for 'Employee No'.")
    padding = fields.Integer("Sequence Size",required = True)
    sequence_id = fields.Many2one('ir.sequence', 'Sequence Name',required = True,ondelete="cascade")

    @api.model
    def create(self,vals):
        company_name = self.env['res.company'].search([('id','=',vals['company_id'])])
    
        emp_type = ((vals['name'].lower()).strip()).replace(" ","_")

        Sequence_id = self.env['ir.sequence'].create({
            'name': emp_type,#company_employment_type
            'prefix': vals['prefix_sequence'],
            'padding': vals['padding'],
            'company_id': vals['company_id'],
            'code':company_name.name + '_' + emp_type,
            })
        
        vals['sequence_id'] = Sequence_id.id
        vals['company_employment_type'] = emp_type
        result = super(CompanyEmploymentType,self).create(vals)
        return result


    def unlink(self):
        for emp_type in self:
            company_history = self.env['company.history'].search([('company_id','=',emp_type.company_id.id),('company_employment_type','=ilike',emp_type.company_employment_type)])
        
            if company_history:
                raise ValidationError(_("Error! Not allowed to delete record with generated 'Employee No'"))
                
            self._cr.execute('delete from ir_sequence where id = '+ str(emp_type.sequence_id.id))
            result = super(CompanyEmploymentType,self).unlink()
            return result