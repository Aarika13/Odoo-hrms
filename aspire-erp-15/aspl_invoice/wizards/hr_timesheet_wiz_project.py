# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
# from odoo import UserError, ValidationError
from odoo.exceptions import UserError
from datetime import timedelta, date
# from datetime import datetime, date
# from odoo import DEFAULT_SERVER_DATE_FORMAT
import datetime
import re
import time
import logging

_logger = logging.getLogger(__name__)


class InvoiceMenu(models.Model):
    _name = "invoice.menu.wizard"
    _description = "invoice Menu Wizard"

    account_ids = fields.Many2many('account.analytic.account','rel_account_analytic_account_invoice_menu_wizard','account_analytic_account_id','invoice_menu_wizard_id', string='Project', required=True,)
    date_from = fields.Date('Date from', select=1, required=True,default=lambda self: self.get_default_start_date())
    date_to = fields.Date('Date to', select=1, required=True,default=lambda self: self.get_default_end_date())
    not_approve_ts = fields.Boolean('Consider not approved Timesheet lines', default=True)
    partner_id = fields.Many2one('res.partner', 'Client', required=True , store=True)
    invoice_tmpl = fields.Many2one('invoice.template.data','Pre-created Invoice', help="To select previously created invoice template(s).")
    tmpl_name = fields.Char(string='New Invoice Name', required=True, store=True , help="To give name to new invoice template.")
    date_format = fields.Many2one('invoice.date.format', string='Date Format', required=True)
    state =fields.Selection([('draft','draft'),('invoice','invoice'),('invoice2','invoice2')],string='State',invisible=True,default='draft')
    invoice_pricing = fields.One2many('invoice.pricing.details','inv_wiz_id',string='Invoice Pricing Details', domain=[('is_timesheet', '=', True)])
    invoice_pricing2 = fields.One2many('invoice.pricing.details','inv_wiz_id',string='Invoice Pricing Details', domain=[('is_timesheet', '=', True)])
    invoice_line_type =fields.Selection([('employee_wise','Employee wise'),('product_wise','Product wise')],string='Invoice line type')
    company_id =fields.Many2one('res.company',default=lambda self: self.env.user.company_id)
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type',default='percent')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2),default=0.00)
    partner_bank_id = fields.Many2one('res.partner.bank', string='Recipient Bank',store=True)
    gst_treatment = fields.Selection([
            ('regular', 'Registered Business - Regular'),
            ('composition', 'Registered Business - Composition'),
            ('unregistered', 'Unregistered Business'),
            ('consumer', 'Consumer'),
            ('overseas', 'Overseas'),
            ('special_economic_zone', 'Special Economic Zone'),
            ('deemed_export', 'Deemed Export')
        ], string="GST Treatment", store=True, readonly=False, default='consumer',required=True)
    
    @api.onchange('company_id')
    def _get_currency_company_banks(self):
        if self.company_id:
            return {"domain":{'partner_bank_id':[('partner_id.name','=',self.company_id.name)]}}
    
    def get_default_start_date(self):
        today = datetime.datetime.now()
        current_month_start = today.replace(day=1)
        prev_month_end = current_month_start - datetime.timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)

        return prev_month_start

    def get_default_end_date(self):
        today = datetime.datetime.now()
        current_month_start = today.replace(day=1)
        prev_month_end = current_month_start - datetime.timedelta(days=1)

        return prev_month_end

    # @api.onchange('invoice_line_type')
    def enter_pricing_timesheet_invoice(self):
        _logger.info('Pricing Account id : %s',self.account_ids)
        account_id_data = self.env['account.analytic.line'].browse(self.account_ids.ids)
    
        if self.invoice_line_type == 'employee_wise':
            invoice_pricing_ids = self.env['invoice.pricing.details'].sudo().search([('inv_wiz_id', '=', self.id),('invoice_line_type','=','employee_wise')])
            self.state='invoice'  # Update the state value from draft to invoice.
        
            if self.not_approve_ts:
                query = "SELECT display_name , sum(unit_amount),product_type FROM public.account_analytic_line where date >= '"+str(self.date_from)+"' and date <= '"+ str(self.date_to) +"' and account_id in "+ str(self.account_ids.ids).replace("[","(").replace("]",")") +" and billable = True and (invoiced != True or invoiced is null) and product_type is not null and unit_amount > '00.00' group by display_name,product_type;"
            else:
                query = "SELECT display_name , sum(unit_amount),product_type FROM public.account_analytic_line where date >= '"+str(self.date_from)+"' and date <= '"+ str(self.date_to) +"' and account_id in "+ str(self.account_ids.ids).replace("[","(").replace("]",")") +" and billable = True and Approved = True and product_type is not null and (invoiced != True or invoiced is null) and unit_amount > '00.00' group by display_name,product_type;"

            _logger.info("Record Query == %s",query)

            # fetch pricing details based on selected invoice template.
            self.env.cr.execute(query)
            row = self.env.cr.fetchone()
            data = []
            user_list = []
            while row is not None:
                d = [row[var] for var in range(len(row))]
                data.append(d)
                user_list.append(d[0])
                row = self.env.cr.fetchone()
                
            if data:
                inv_price_obj =self.env['invoice.pricing.details']
                
                price_line_list = []
                for user in data:
                    user_price_line = inv_price_obj.sudo().search([('inv_wiz_id', '=', self.invoice_tmpl.inv_wiz_id.id), ('inv_wiz_id','!=',False),('invoice_line_type','=','employee_wise'),('user_id','=',user[0]),('product_id','=',user[2])])
                    price_line_list.append(user_price_line.id)

                if len(price_line_list)>1:
                    pricing_ids = inv_price_obj.browse(price_line_list[0])
                else:
                    pricing_ids = inv_price_obj.browse(price_line_list)
                
                self.invoice_pricing = pricing_ids

                if pricing_ids:
                    self.invoice_tmpl.inv_wiz_id = self.id

                for pricing_id in pricing_ids:
                    pricing_id.write({
                        'inv_wiz_id':self.id
                        })


                #Added code to pre-fill pricing details for new record.
                for user_data in data:   
                    emp_price_line_id = inv_price_obj.sudo().search([('inv_wiz_id', '=', self.invoice_tmpl.inv_wiz_id.id), ('inv_wiz_id','!=',False),('invoice_line_type','=','employee_wise'), ('user_id','=',user_data[0]),('product_id','=',user_data[2])])
                    
                    if emp_price_line_id:
                        emp_price_line_id.write({'emp_total_hr': user_data[1]})
                    else:
                        self.pre_fill_pricing_details(user_data,inv_price_obj)

                #Added code to fill up previous wizard id in pricing and template data.
                invoice_templates = self.env['invoice.template.data'].search([('inv_wiz_id', '=', self.id)])
                for inv_tmpl in invoice_templates:
                    if self.invoice_tmpl.id != inv_tmpl.id:
                        pre_invoice_wiz_id = self.sudo().search([('invoice_tmpl', '=', inv_tmpl.id)], order="id desc", limit=1)
                        inv_tmpl.sudo().write({'inv_wiz_id':pre_invoice_wiz_id.id})
                        invoice_pricing_ids.sudo().write({'inv_wiz_id':pre_invoice_wiz_id.id})
            else:
                raise UserError("No analytic lines to create invoiceSorry! No Timesheet lines are found for the project to Invoice.")
        else:

            if self.not_approve_ts:
                query = "SELECT product_type , sum(unit_amount),string_agg( CAST(id as varchar(25)),',') FROM public.account_analytic_line where date >= '"+str(self.date_from)+"' and date <= '"+ str(self.date_to) +"' and account_id in "+ str(self.account_ids.ids).replace("[","(").replace("]",")") +" and billable = True and product_type is not null and (invoiced != True or invoiced is null) and unit_amount > '00.00' group by product_type;"
            else:
                query = "SELECT product_type , sum(unit_amount),string_agg( CAST(id as varchar(25)),',') FROM public.account_analytic_line where date >= '"+str(self.date_from)+"' and date <= '"+ str(self.date_to) +"' and account_id in "+ str(self.account_ids.ids).replace("[","(").replace("]",")") +" and billable = True  and (invoiced != True or invoiced is null) and product_type is not null and Approved = True and unit_amount > '00.00' group by product_type;"
            
            _logger.info("Record Query == %s",query)

            # fetch pricing details based on selected invoice template.
            self.env.cr.execute(query)
            row = self.env.cr.fetchone()
            data = []
            product_list = []
            while row is not None:
                d = [row[var] for var in range(len(row))]
                data.append(d)
                product_list.append(d[0])
                row = self.env.cr.fetchone()
            if data:
                invoice_pricing_ids = self.env['invoice.pricing.details'].sudo().search([('inv_wiz_id', '=', self.invoice_tmpl.inv_wiz_id.id),('invoice_line_type','=','product_wise')])
                self.state='invoice2'  # Update the state value from draft to invoice.

                # fetch pricing details based on selected invoice template.
                inv_price_obj = self.env['invoice.pricing.details']
                pricing_line_ids = inv_price_obj.sudo().search([('inv_wiz_id', '=', self.invoice_tmpl.inv_wiz_id.id), ('inv_wiz_id','!=',False),('invoice_line_type','=','product_wise'),('product_id','in',product_list)])
                line_ids = []
                product_ids = []
                for price_line in pricing_line_ids:
                    if price_line.product_id.id not in product_ids:
                        product_ids.append(price_line.product_id.id)
                        line_ids.append(price_line.id)

                pricing_ids = inv_price_obj.browse(line_ids)

                self.invoice_pricing2 = pricing_ids

                if pricing_ids:
                    self.invoice_tmpl.inv_wiz_id = self.id
                    for pricing_id in pricing_ids:
                        pricing_id.write({
                            'inv_wiz_id':self.id
                            })
                for product_data in data:
                    product_price_line_id = inv_price_obj.sudo().search([('inv_wiz_id', '=', self.invoice_tmpl.inv_wiz_id.id), ('inv_wiz_id','!=',False),('invoice_line_type','=','product_wise'), ('product_id','=',product_data[0])])
                    if product_price_line_id:
                        product_price_line_id.write({'emp_total_hr': product_data[1],
                            'analytic_line_ids':product_data[2]})
                    else:
                        self.pre_fill_pricing_details_product(product_data,inv_price_obj)
            else:
                raise UserError("Sorry! No Timesheet lines are found for the project to Invoice.")
        
        return {
            'res_model': 'invoice.menu.wizard',
            'view_mode': 'form',
            'name':"Generate Invoice",
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
        }

    @api.model
    def pre_fill_pricing_details(self,user_data,inv_price_obj):
        '''
        Added code to pre-fill pricing details for new record.
        :param emp: employee id
        :return:
        '''
        user_obj = self.env['res.users'].browse(user_data[0])
        
        if user_obj.active == True and user_data[2]:
            id_data = inv_price_obj.sudo().create({
                'inv_wiz_id': self.id,
                'user_id': user_data[0],
                'price':0,
                'product_id' : user_data[2],
                'emp_total_hr': user_data[1],
                'invoice_line_type': self.invoice_line_type,
            })

        else:
            raise UserError("Please! Add Product In Timesheet Entry From " + str(datetime.datetime.strptime(str(self.date_from), '%Y-%m-%d').strftime('%d/%m/%Y')) + " to " + str(datetime.datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime('%d/%m/%Y')))



    @api.model
    def pre_fill_pricing_details_product(self,product_data,inv_price_obj):
        if product_data[0]:

            inv_price_obj.create({
                'inv_wiz_id': self.id,
                'price':0,
                'quantity':1,
                'product_id' : product_data[0],
                'emp_total_hr': product_data[1],
                'invoice_line_type': self.invoice_line_type,
                'analytic_line_ids':str(product_data[2])
            })
        else:
            raise UserError("Please! Add Product In Timesheet Entry From " + str(datetime.datetime.strptime(str(self.date_from), '%Y-%m-%d').strftime('%d/%m/%Y')) + " to " + str(datetime.datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime('%d/%m/%Y')))


    # @api.onchange('date_format')
    def onchange_date_format(self):
        date_list = []
        inv_date_format = ''
        date_format = self.date_format.name
        date_format = str(date_format)
        if date_format != 'False':
            separator = re.split(r"[\w']+",date_format) # Split separator from date format
            date = re.findall(r"[\w']+",date_format) # Split month,day and year from date format

            # Append month,day and year in date_list
            date_list.append(date[0])
            date_list.append(date[1])
            date_list.append(date[2])

            # Replace month/day/year to display date as per python date strftime date format
            temp_date_list = [list.replace('mmmm', 'B') for list in date_list]
            temp_date_list1 = [list.replace('mmm', 'b') for list in temp_date_list]
            temp_date_list2 = [list.replace('m', '-m') for list in temp_date_list1]
            temp_date_list3 = [list.replace('mm', 'm') for list in temp_date_list2]
            temp_date_list4 = [list.replace('d', '-d') for list in temp_date_list3]
            temp_date_list5 = [list.replace('dd', 'd') for list in temp_date_list4]
            temp_date_list6 = [list.replace('-d-d', 'd') for list in temp_date_list5]
            temp_date_list7 = [list.replace('-m-m', 'm') for list in temp_date_list6]
            final_date_list = [list.replace('yyyy', 'Y') for list in temp_date_list7]

            # Merge separator and month/day/year from final_date_list to prepare proper date format
            # if 'B' in final_date_list or 'b' in final_date_list:
            #     if final_date_list[0] == 'b' or final_date_list[0] == 'B':
            #         inv_date_format = '%' + final_date_list[0] + ' ' +'%' + final_date_list[1] + ', ' + '%' + final_date_list[2]
            #     elif final_date_list[1] == 'b' or final_date_list[1] == 'B':
            #         inv_date_format = '%' + final_date_list[0] + ' ' + '%' + final_date_list[1] + ' ' + '%' + final_date_list[2]
            # else:
            inv_date_format = '%' + final_date_list[0] + separator[1] + '%' + final_date_list[1] + separator[2] + '%' + \
                              final_date_list[2]

            return inv_date_format

    # To fill project,client and journal information based on selected invoice template.
    @api.onchange('invoice_tmpl')
    def _onchange_inv_wiz_data(self):
        self.partner_id = self.invoice_tmpl.partner_id
        self.invoice_line_type= self.invoice_tmpl.invoice_line_type
        self.account_ids= self.invoice_tmpl.account_ids
        self.tmpl_name = self.invoice_tmpl.name
        self.invoice_line_type = self.invoice_tmpl.invoice_line_type
        self.partner_bank_id = self.invoice_tmpl.partner_bank_id
        # self.wire_selection = self.invoice_tmpl.wire_selection
        # self.wire_info = self.invoice_tmpl.wire_info
        self.date_format = self.invoice_tmpl.date_format
        self.discount_rate = self.invoice_tmpl.discount_rate
        self.discount_type = self.invoice_tmpl.discount_type
        self.company_id = self.invoice_tmpl.company_id if self.invoice_tmpl.company_id else self.env.company.id

#     #Action for back button in wizard.
#     @api.multi
#     def action_previous(self):
#         self.write({'state': 'draft'})
#         # return view
#         return {
#             'type': 'ir.actions.act_window',
#             'res_model': 'invoice.menu.wizard',
#             'view_mode': 'form',
#             'view_type': 'form',
#             'res_id': self.id,
#             'views': [(False, 'form')],
#             'target': 'new',
#             'view_id': self.id,
#         }


    def action_previous_state(self):
        self.write({'state': 'draft'})
        # return view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'invoice.menu.wizard',
            'name':"Generate Invoice",
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
            'view_id': self.id,
        }
    
    def create_invoice(self):
        invoice_id=None
        invoice = self.env['account.move']
        _logger.info('invoice create_invoice : %s',invoice)
        userObj = self.env['res.users']
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].sudo().browse(current_uid)
        invoice_date = ''
        current_date = fields.Date.context_today(self)
        inv_date_format = self.onchange_date_format()

        journal_id =  self.env['account.journal'].sudo().search([('company_id','=',self.company_id.id),('name','like','Customer Invoices')])
        _logger.info('journal_id create_invoice : %s',journal_id)

        if not journal_id:
            raise UserError("Please create customer Invoices general.")
        if not self.partner_id.currency:
            raise UserError("Please set 'Currency' in the customer.")
        elif not self.partner_id.payment_detial:
            raise UserError("Please add 'Payment Swift Details' in the customer.")
        elif not self.partner_id.property_account_receivable_id:
            raise UserError("Please set 'Accounts' in the customer.")
        elif not self.partner_id.property_payment_term_id:
            raise UserError("Please set 'Payment Terms' in the customer.")
        else:
            try:
                invoice_id = self.env['account.move'].create({
                    'partner_id':self.partner_id.id,
                    # 'partner_shipping_id':self.partner_id.id,
                    'currency_id':self.partner_id.currency.id,
                    'invoice_date':date.today(),
                    'payment_swift_id':self.partner_id.payment_detial.id,
                    # 'l10n_in_gst_treatment':self.gst_treatment,
                    'move_type':'out_invoice',
                    'l10n_in_gst_treatment':self.partner_id.l10n_in_gst_treatment,
                    'partner_bank_id':self.partner_bank_id,
                    # 'account_id':self.partner_id.property_account_receivable_id.id,
                    # 'state':'draft',
                    'company_id':user.company_id.id,
                    # 'payment_term_id':self.partner_id.property_payment_term_id.id,
                    # 'reference_type': "none",
                    'invoice_payment_term_id':self.partner_id.property_payment_term_id.id,
                    'discount_type' : self.discount_type,
                    'discount_rate' : self.discount_rate,
                    'date_format':inv_date_format,
                    'journal_id': journal_id.id,
                    })
            except Exception as e:
                _logger.error(str(e))

            _logger.info('invoice_id : %s',invoice_id)
            return invoice_id
        


    def create_invoices(self):
        _logger.info('create_invoices : %s',self)
        timesheet_lines = None
        need_to_remove_price_list = []
        invoice = None
        invoice_pricing_details = self.env['invoice.pricing.details']
        invoice_pricing_ids = invoice_pricing_details.sudo().search([('inv_wiz_id','=', self.id),('is_disable','=',False)])
        _logger.info('invoice_pricing_ids : %s',invoice_pricing_ids)
        start_date_inputed = self.date_from
        end_date_inputed = self.date_to
        project_data = None
        product_list = []
        for price_lines in invoice_pricing_ids:
            if self.invoice_line_type == "product_wise":
                if price_lines.product_id not in product_list:
                    product_list.append(price_lines.product_id)
                    price_lines.write({
                        'inv_wiz_id':self.id
                        })
                else:
                    need_to_remove_price_list.append(price_lines.id)
                    continue
        
        _logger.info('need_to_remove_price_list : %s',need_to_remove_price_list)

        if not need_to_remove_price_list:
            invoice = self.create_invoice()
            for price_lines in invoice_pricing_ids:
                if price_lines.analytic_line_ids:
                    update_product_query = "UPDATE public.account_analytic_line SET product_type="+str(price_lines.product_id.id)+" WHERE  id in ("+price_lines.analytic_line_ids+");"
                    self.env.cr.execute(update_product_query)
        else:
            # self.state = 'invoice'
            return {
            'name': 'confirmation',
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'need_to_remove_price_list': need_to_remove_price_list} 
            }

        if invoice:
            product_list = []

            discount = self.discount_count(invoice_pricing_ids)

            for price_lines in invoice_pricing_ids:
                invoice_line = self.env['account.move.line']
                product_id = None
                product_hsn_or_sac_code = None
                price_unit = None
                tempComment = None
                create_invoice_line = None

                if price_lines.invoice_line_type == "employee_wise":
                    self.env.cr.execute("SELECT DISTINCT account_id FROM public.account_analytic_line where display_name = "+str(price_lines.user_id.id)+" and product_type = "+str(price_lines.product_id.id)+";")
                    row = self.env.cr.fetchone()
                    project_data = self.env['project.project'].sudo().search([('analytic_account_id','in',[row[var] for var in range(len(row))])])
                product_id = price_lines.product_id.id
                _logger.info('price_lines : %s',price_lines.product_id)
                if not price_lines.product_id.l10n_in_hsn_code:
                    raise UserError("Please set 'HSN/SAC Code' in the product.")
                else:
                    product_hsn_or_sac_code = price_lines.product_id.l10n_in_hsn_code
                price_unit = price_lines.price
                if not price_lines.product_id.property_account_income_id:
                    raise UserError("Please set 'Income Accounts' in the product.")
                else:
                    account_id = price_lines.product_id.property_account_income_id
                invoice_id = invoice.id

                if self.invoice_line_type == 'employee_wise':
                    if self.not_approve_ts:
                        timesheet_lines = self.env['account.analytic.line'].sudo().search(
                                [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('billable', '=', True),
                                 ('account_id', 'in', self.account_ids.ids), ('display_name', '=', price_lines.user_id.id),
                                 ('invoiced', '=', False),('product_type','=',price_lines.product_id.id)])
                    else:
                        timesheet_lines = self.env['account.analytic.line'].sudo().search(
                                [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('billable', '=', True),
                                 ('account_id', 'in', self.account_ids.ids), ('display_name', '=', price_lines.user_id.id),
                                 ('invoiced', '=', False),('approved', '=', True),('product_type','=',price_lines.product_id.id)])
                    
                    
                    _logger.info("TempComment User == %s",str(price_lines.user_id.name))
                    _logger.info("TempComment Project == %s",str(project_data.name))
                    _logger.info("TempComment Date Format == %s",str(invoice.date_format))
                    _logger.info("TempComment Date From == %s",str(self.date_from))
                    _logger.info("TempComment Date To== %s",str(self.date_to))
                    tempComment= 'Software Consultancy Services provided by '+ str(price_lines.user_id.name)+' '+str('on')+' '+str(project_data.name)+' '+str('from')+' '+ str(datetime.datetime.strptime(str(self.date_from), '%Y-%m-%d').strftime(invoice.date_format))+ ' to '+ str(datetime.datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime(invoice.date_format))
                    _logger.info("TempComment Date To== %s",tempComment)

                    time = price_lines.emp_total_hr
                else:
                    if self.not_approve_ts:
                        timesheet_lines = self.env['account.analytic.line'].sudo().search(
                                [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('billable', '=', True),
                                 ('account_id', 'in', self.account_ids.ids), ('product_type', '=', price_lines.product_id.id),
                                 ('invoiced', '=', False)])
                    else:
                        timesheet_lines = self.env['account.analytic.line'].sudo().search(
                                [('date', '>=', self.date_from), ('date', '<=', self.date_to), ('billable', '=', True),
                                 ('account_id', 'in', self.account_ids.ids), ('product_type', '=', price_lines.product_id.id),
                                 ('invoiced', '=', False),('approved', '=', True)])

                    _logger.info("TempComment Project == %s",price_lines.product_id.name)
                    _logger.info("TempComment Date Format == %s",str(invoice.date_format))
                    _logger.info("TempComment Date From == %s",str(self.date_from))
                    _logger.info("TempComment Date To== %s",str(self.date_to))
                    tempComment= 'Software Consultancy Services provided from ' + str(datetime.datetime.strptime(str(self.date_from), '%Y-%m-%d').strftime(invoice.date_format))+ ' to '+ str(datetime.datetime.strptime(str(self.date_to), '%Y-%m-%d').strftime(invoice.date_format)) + ' - ' + str(price_lines.product_id.name)
                    _logger.info("TempComment Date To== %s",tempComment)
                    time = price_lines.quantity
                
                try: 
                    create_invoice_line = invoice.write({
                        # 'l10n_in_gst_treatment':self.gst_treatment,
                        'invoice_line_ids':[(0,0,{
                        'product_id':product_id,
                        'analytic_account_id':timesheet_lines.account_id.id,
                        'product_hsn_or_sac_code':product_hsn_or_sac_code,
                        'price_unit':price_unit,
                        'account_id':account_id.id,
                        'quantity':time,
                        'name': tempComment,
                        'move_id': invoice_id,
                        'tax_ids' : [(6, 0, [tax.id for tax in self.partner_id.tax_ids])],
                        'discount': discount,
                    })]
                    })
                    
                except Exception as e:
                    _logger.error(str(e))      
    
                #To create tax line on the basis of selected customer in invoice.                        
                invoice_line_tax_vals = {}
                if invoice.invoice_line_ids and invoice.invoice_line_ids.tax_ids:
                    for tax_line_id in invoice.invoice_line_ids.tax_ids:
                        try:
                            invoice_line_tax_vals.sudo().update({
                                                    'account_id' : invoice.type in ('out_invoice', 'in_invoice') and (tax_line_id.account_id.id or create_invoice_line.account_id.id) or (tax['refund_account_id'] or create_invoice_line.account_id.id),
                                                    'sequence': tax_line_id.sequence,
                                                    'invoice_id': invoice.id,
                                                    'amount': (invoice.invoice_line_ids.original_amount * tax_line_id.amount)/100,
                                                    'tax_id': tax_line_id.id,
                                                    'name' : tax_line_id.name,
                                                })
                            test =  (invoice.amount_untaxed * tax_line_id.amount)/100
                            create_tax_line = self.env['account.invoice.tax'].create(invoice_line_tax_vals)
                        except Exception as e:
                            _logger.error(str(e))

                # self.add_discount(invoice)
                for lines in timesheet_lines:
                    lines.sudo().write({'invoiced':True,'invoice_id':invoice_id})

            vals = {}
            vals.update({
                'partner_id': self.partner_id.id,
                'name': self.tmpl_name,
                'invoice_line_type':self.invoice_line_type,
                'date_format':self.date_format.id,
                'discount_rate':self.discount_rate,
                'discount_type':self.discount_type,
                'partner_bank_id': self.partner_bank_id.id,
                'company_id':self.company_id.id,
                # 'gst_treatment': self.gst_treatment,
            })
            vals.update(account_ids = [(6,0,[project.id for project in self.account_ids])])
            # To store invoice wizard id in template for pricing details reference.
            for inv_pricing_ids in invoice_pricing_ids:
                inv_pricing_id = self.env['invoice.pricing.details'].sudo().browse(
                    inv_pricing_ids.id)
                vals.update({
                    'inv_wiz_id':inv_pricing_id.inv_wiz_id.id
                })

            if self.invoice_tmpl:
                update_invoice_data = self.invoice_tmpl.sudo().write(vals) # Update existing template if exist
            else:
                create_invoice_data= self.invoice_tmpl.create(vals) # Create new invoice template

            self.env.cr.execute("DELETE FROM public.invoice_pricing_details WHERE inv_wiz_id is null;")

        def get_view_id(xid, name):
            try:
                return self.env.ref('account.' + xid)
            except ValueError:
                view = self.env['ir.ui.view'].search([('name', '=', name)], limit=1)
                if not view:
                    return False
                return view.id

  
        if invoice:
            return {
                'name':_('Invoices'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'view_id' : get_view_id('view_move_form', 'account.move.form').id
            }


    def discount_count(self,invoice_pricing_ids):
        total = 0.0
        for price_line in invoice_pricing_ids:
            current_total = price_line.emp_total_hr * price_line.price
            total += current_total
        
        if self.discount_type == 'percent':
            return self.discount_rate
        else:
            return ((self.discount_rate / total) * 100)

    # def add_discount(self,invoice):
    #     for inv in invoice:
    #         if inv.discount_type == 'percent':
    #             for line in inv.invoice_line_ids:
    #                 # line = line.with_context(check_move_validity = False)
    #                 line.write({'discount':inv.discount_rate})
                    
    #         else:
    #             total = discount = 0.0
    #             for line in inv.invoice_line_ids:
    #                 total += (line.quantity * line.price_unit)
    #             if inv.discount_rate != 0:
    #                 discount = (inv.discount_rate / total) * 100
    #             else:
    #                 discount = inv.discount_rate
    #             for line in inv.invoice_line_ids:
    #                 # line.discount = discount
    #                 line.write({'discount':discount})


#     def find_date_array_from_start_end_date(self,start_date,end_date):
#         day = start_date.weekday()
#         en_date = start_date
#         if day == 6:
#             en_date = start_date+datetime.timedelta(days=6)
#         else:
#             timedelta_day = 5 - int(day)
#             en_date = start_date+datetime.timedelta(days=timedelta_day)
#         date_array = []
#         if en_date>end_date:
#             date_str = str(start_date)+","+str(end_date)
#         else:
#             date_str = str(start_date)+","+str(en_date)
#         date_array.append(date_str)


#         while en_date<=end_date:
#             next_date = en_date+datetime.timedelta(days=1)
#             next_weekend_date = next_date+datetime.timedelta(days=6)
#             if next_date<=end_date:

#                 if next_weekend_date>end_date:
#                     date_end_str = str(next_date)+","+str(end_date)
#                 else:
#                     date_end_str = str(next_date)+","+str(next_weekend_date)
#                 date_array.append(date_end_str)
#                 en_date = next_weekend_date
#             else:
#                 break
#         return date_array

class InvoiceTmplData(models.Model):
    _name = "invoice.template.data"
    _description = "invoice Template Data"

    name = fields.Char(string='Template Name')
    account_ids = fields.Many2many('account.analytic.account','rel_account_analytic_account_invoice_template_data','analytic_account_ids','invoice_template_data_id', string='Project',store=True,help="Projects")
    partner_id = fields.Many2one('res.partner', 'Client',store=True,help="Customer")
    invoice_line_type =fields.Selection([('employee_wise','Employee wise'),('product_wise','Product wise')],string='Invoice line type')
    date_format = fields.Many2one('invoice.date.format', string='Date Format')
    inv_wiz_id = fields.Many2one('invoice.menu.wizard','Invoice Pricing Details')
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2))
    partner_bank_id = fields.Many2one('res.partner.bank', string="Recipient Bank Account" )
    company_id = fields.Many2one('res.company',string="Company")
    

class InvoicePricingDetails(models.Model):
    _name = "invoice.pricing.details"
    _description = "invoice Pricing Details"

    user_id = fields.Many2one('res.users', string='Users')
    inv_wiz_id = fields.Many2one('invoice.menu.wizard', string='Invoice Wizard ID')
    price = fields.Float('Unit Price')
    quantity = fields.Float('Quantity')
    emp_total_hr = fields.Float('Total Hours',readonly=True)
    is_disable = fields.Boolean('Is Disable',default = False)
    is_timesheet = fields.Boolean('Is Timesheet',default = True)
    product_id = fields.Many2one("product.product","Product")
    invoice_line_type =fields.Selection([('employee_wise','Employee wise'),('product_wise','Product wise')],string='Invoice line type')
    analytic_line_ids = fields.Text('Activiy Line Ids')

    #Create new pricing line and delete existing pricing line for employee
    @api.model
    def create(self,vals):
        if vals.get('invoice_line_type') == 'employee_wise':
            invoice_pricing_line_ids=self.env['invoice.pricing.details'].sudo().search([('user_id','=',vals.get("user_id")),('inv_wiz_id','=',vals.get("inv_wiz_id")),('product_id','=',vals.get("product_id"))])
            if invoice_pricing_line_ids:
                for line_id in invoice_pricing_line_ids:
                    line_id.sudo().unlink()
        else:
            invoice_pricing_line_ids=self.env['invoice.pricing.details'].sudo().search([('product_id','=',vals.get("product_id")),('inv_wiz_id','=',vals.get("inv_wiz_id"))])
            if invoice_pricing_line_ids:
                for line_id in invoice_pricing_line_ids:
                    line_id.sudo().unlink()
        if 'user_id' not in vals and 'product_id' not in vals:
            vals=[]
        return super(InvoicePricingDetails, self.sudo()).create(vals) 
    
    @api.onchange('user_id','product_id')
    def onchange_add_items(self):
        timesheet_lines = None
        total = 0.0
        if self.inv_wiz_id.invoice_line_type == 'employee_wise' and self.user_id and self.product_id:
            if self.inv_wiz_id.not_approve_ts :
                timesheet_lines = self.env['account.analytic.line'].sudo().search(
                [('date', '>=', self.inv_wiz_id.date_from), ('date', '<=', self.inv_wiz_id.date_to), ('billable', '=', True),
                ('account_id', 'in', self.inv_wiz_id.account_ids.ids), ('display_name', '=', self.user_id.id),('product_type','=',self.product_id.id),
                ('invoiced', '=', False)])
            else:            
                timesheet_lines = self.env['account.analytic.line'].sudo().search(
                [('date', '>=', self.inv_wiz_id.date_from), ('date', '<=', self.inv_wiz_id.date_to), ('billable', '=', True),
                ('account_id', 'in', self.inv_wiz_id.account_ids.ids), ('display_name', '=', self.user_id.id),('product_type','=',self.product_id.id),
                ('invoiced', '=', False),('approved', '=', True)])
        elif self.inv_wiz_id.invoice_line_type == 'product_wise' and self.product_id and not self.emp_total_hr:
            if self.inv_wiz_id.not_approve_ts:
                timesheet_lines = self.env['account.analytic.line'].sudo().search(
                [('date', '>=', self.inv_wiz_id.date_from), ('date', '<=', self.inv_wiz_id.date_to), ('billable', '=', True),
                ('account_id', 'in', self.inv_wiz_id.account_ids.ids),('product_type', '=', self.product_id.id),
                ('invoiced', '=', False)])
            else:            
                timesheet_lines = self.env['account.analytic.line'].sudo().search(
                [('date', '>=', self.inv_wiz_id.date_from), ('date', '<=', self.inv_wiz_id.date_to), ('billable', '=', True),
                ('account_id', 'in', self.inv_wiz_id.account_ids.ids),('product_type', '=', self.product_id.id),
                ('invoiced', '=', False),('approved', '=', True)])

        if timesheet_lines is not None:
            for record in timesheet_lines:
                total+=record.unit_amount
            self.emp_total_hr = total
            self.quantity = 1.0