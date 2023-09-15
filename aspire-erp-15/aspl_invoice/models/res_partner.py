from odoo import api, fields, models, _
from odoo import tools, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class res_partner(models.Model):
    _inherit = 'res.partner'
    
    payment_detial = fields.Many2one('payment.swift.details',"Payment Instruction", domain="[('currency', '=', currency )]")
    tax_ids =  fields.Many2many('account.tax', 'partner_tax_rel', 'partner_id', 'tax_id', string='Tax')
    state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    country_id =  fields.Many2one('res.country', 'Country', ondelete='restrict')
    pan_no = fields.Char('PAN NO')
    currency = fields.Many2one('res.currency',"Currency",domain=[('active', '=', True)])
    v9_id = fields.Integer('Odoo9 Partner')
    
    # @api.onchange('company_id','country_id')
    # def on_change_company_id(self):
    #     for record in self:
    #         if record.company_id:
    #             account_receivable = self.env['account.account'].search([('company_id','=',record.company_id.id),('internal_type', '=', 'receivable'), ('deprecated', '=', False)])
    #             account_payable = self.env['account.account'].search([('company_id','=',record.company_id.id),('internal_type', '=', 'payable'), ('deprecated', '=', False)])
    #             if account_receivable:
    #                 record.property_account_receivable_id = account_receivable
    #             else:
    #                 raise UserError(_('Please create Account Receivable for ' + record.company_id.name))

    #             if account_payable:
    #                 record.property_account_payable_id = account_payable
    #             else:
    #                 raise UserError(_('Please create Account Payable for ' + record.company_id.name))
                    
    #             if record.state_id and record.customer and record.state_id.country_id.code == 'IN' and record.company_id.GST_No:
    #                 if record.state_id.name == 'Gujarat':
    #                     taxIds =  self.env['account.tax'].search([('description','in',('CGST @ 9%','SGST @ 9%')),('company_id','=',record.company_id.id)])
    #                     if taxIds:
    #                         record.tax_ids = taxIds
    #                     else:
    #                         record.tax_ids = False
    #                         raise UserError(_('Please create Account tax for ' + record.company_id.name))
    #                 else:
    #                     taxIds =  self.env['account.tax'].search([('description','=','IGST @ 18%'),('company_id','=',record.company_id.id)])
    #                     if taxIds:
    #                         record.tax_ids = taxIds
    #                     else:
    #                         record.tax_ids = False
    #                         raise UserError(_('Please create Account tax for ' + record.company_id.name))
    #             else:
    #                 record.tax_ids = False




    # def write(self, vals,context=None):
    #     if vals.get('state_id'):
    #         stateData = self.pool.get('res.country.state').browse([vals.get('state_id')])
    #         if stateData.country_id.code == 'IN' and self.browse(ids).customer and self.browse(ids).company_id.GST_No:
    #             if stateData.name == 'Gujarat':
    #                 taxIds =  self.pool.get('account.tax').search([('description','in',('CGST @ 9%','SGST @ 9%')),('company_id','=',self.browse(cr,uid,ids).company_id.id)])
    #                 if taxIds:
    #                     vals['tax_ids'] = [(6, 0, taxIds)]
    #                 else:
    #                     raise UserError(_('Please create Account tax for ' + self.browse(ids).company_id.name))
    #             else:
    #                 taxIds =  self.pool.get('account.tax').search(cr,uid,[('description','=','IGST @ 18%'),('company_id','=',self.browse(cr,uid,ids).company_id.id)])
    #                 if taxIds:
    #                     vals['tax_ids'] = [(6, 0, taxIds)]
    #                 else:
    #                     raise UserError(_('Please create Account tax for ' + self.browse(cr,uid,ids).company_id.name))
        
    #     if vals.get('child_ids'):
    #         if not self.validatePartner(cr, uid, vals, context=None):
    #             raise UserError(_("There can be only one invoice contact per customer."))
    #     res = super(res_partner, self).write(cr, uid, ids, vals, context=context)
    #     return res



    # def create(self, cr, uid, data, context=None):
    #     if data.get('child_ids'):
    #         if not self.validatePartner(cr, uid, data, context=None):
    #             raise UserError(_("There can be only one invoice contact per customer."))
    #     res = super(res_partner, self).create(cr, uid, data, context=context)
    #     return res



    def validatePartner(self, cr, uid, data, context=None):
        if data.get('child_ids'):
            temp = []
            for i in range(len(data['child_ids'])):
                if data['child_ids'][i][0] != 1 and data['child_ids'][i][1] and self.browse(cr,uid,[data['child_ids'][i][1]]) and self.browse(cr,uid,[data['child_ids'][i][1]]).type == 'invoice':
                    temp.append(i)
                    continue
                if data['child_ids'][i][2] and 'type' in data['child_ids'][i][2] and data['child_ids'][i][2].get('type') == 'invoice':
                    temp.append(i)
                    continue
            if len(temp) != 0 and len(temp) > 1:
                return False
        return True
