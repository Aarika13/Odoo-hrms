
from odoo import api, exceptions, models, _, fields
from odoo.tools.translate import _
from odoo.exceptions import UserError,ValidationError
from datetime import datetime, date
import logging
import traceback
import re
from odoo.http import request

_logger = logging.getLogger(__name__)

# class ProductTemplate(models.Model):
#     _inherit = 'product.template'

#     gst_service_code = fields.Many2one('product.gst.code',"GST Service Code",required=True)

class ProductGSTCode(models.Model):
    _name = 'product.gst.code'
    _description = "Product Gst Code"

    name = fields.Char("GST Service Code",required=True)
    description = fields.Char("Description")

    @api.model
    def create(self,vals):
        gst_code = vals['name']
        pattern  = '^(?=.*[a-zA-Z])(?=.*[0-9])'
        if (re.search(pattern,gst_code)) and len(gst_code) == 15:
            return super(ProductGSTCode,self).create(vals)
        else:
            raise UserError(_("Please! Enter Correct GST Number."))


    def write(self,vals):
        gst_code = vals['name']
        pattern  = '^(?=.*[a-zA-Z])(?=.*[0-9])'
        if (re.search(pattern,gst_code)) and len(gst_code) == 15:
            return super(ProductGSTCode,self).write(vals)
        else:
            raise UserError(_("Please! Enter Correct GST Number."))     

class Project(models.Model):
    _inherit = 'project.project'

    product_id = fields.Many2many(comodel_name ='product.product',string="Product") 

class AccountAnalyticLineExtend(models.Model):
    _inherit = 'account.analytic.line'
 
    def _get_project_product(self):
        context = self._context
        
        if 'active_id' in context:
            project = context['active_id']
            project_id = self.env['project.project'].browse(project)
            domain =[('id', 'in', project_id.product_id.ids)]

        else:
            domain =[('id', 'in',[])]

        return domain

    def _set_default_product(self):
        account_line = request.jsonrequest
        if 'args' in account_line['params'] and len(account_line['params']['args']) > 1:
            if 'task_id' in account_line['params']['args'][1]:
                context = self._context
                current_uid = context.get('uid')
                task_id = account_line['params']['args'][1]['task_id']['id']
                if task_id:
                    analytic_line_id = self.env['account.analytic.line'].search([('task_id','=',task_id),('user_id','=',current_uid)],limit=1, order='id desc')
                    if analytic_line_id.product_type:
                        return analytic_line_id.product_type.id
                    else:
                        analytic_line_project_id = self.env['account.analytic.line'].search([('task_id.project_id','=',self.env.context['default_project_id']),('user_id','=',current_uid)],limit=1, order='id desc')
                        if analytic_line_project_id.product_type:
                            return analytic_line_project_id.product_type.id
                        else:
                            product_id = self.env['project.project'].browse(self.env.context['default_project_id']).product_id
                            return product_id.ids[0] if len(product_id.ids) >= 1  else ''
                    
                elif 'default_project_id' in self.env.context:
                    analytic_line_id = self.env['account.analytic.line'].search([('task_id.project_id','=',self.env.context['default_project_id']),('user_id','=',current_uid)],limit=1, order='id desc')
                    if analytic_line_id.product_type:
                        return analytic_line_id.product_type.id
                    else:
                        product_id = self.env['project.project'].browse(self.env.context['default_project_id']).product_id
                        return product_id.ids[0] if len(product_id.ids) >= 1  else ''

    product_type = fields.Many2one("product.product", domain=_get_project_product,string="Product",default =lambda self: self._set_default_product())

    @api.onchange('project_id')
    def get_default_product_type(self):
        product_id = self.project_id.product_id
        if product_id:
            return {"domain":{'product_type':[('id','in',self.project_id.product_id.ids)]}}

    
    def get_product(self):
        # product_id = []
        project_id = []
        for analytic_line in self:
            # if analytic_line.product_type and analytic_line.product_type.id not in product_id:
            #     product_id.append(analytic_line.product_type.id)
            if analytic_line.project_id.id not in project_id:
                project_id.append(analytic_line.project_id.id)

        if len(project_id) > 1:
            raise ValidationError(_('Please confirm ! project must be same.'))
        
        if self.project_id.product_id.ids:
            product_id = self.project_id.product_id.ids
        else:
            raise ValidationError(_("Kindly add 'Product' in "+ self.project_id.name + " project."))

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'timesheet.product.change',
            'view_type':'form',
            'view_mode':'form',
            'name':_('Timesheet Product Change'),
            'target':'new',
            'context': {'product_id': product_id,'account_analytic_ids':self.ids},
        }