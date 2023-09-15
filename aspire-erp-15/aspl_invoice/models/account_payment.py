import json
import re
import time
import math
import logging
from odoo import exceptions
from odoo import tools
from odoo import models, fields, api, _
from odoo.osv import osv
from odoo.tools import float_round, float_is_zero, float_compare
from odoo.exceptions import ValidationError
from datetime import datetime, time ,date,timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime,timedelta,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_TIME_FORMAT


CURRENCY_DISPLAY_PATTERN = re.compile(r'(\w+)\s*(?:\((.*)\))?')

_logger = logging.getLogger(__name__)
_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'weeks': lambda interval: relativedelta(days=7*interval),
    'months': lambda interval: relativedelta(months=interval),
}

# mapping invoice type to journal type
TYPE2JOURNAL = {
    'out_invoice': 'sale',
    'in_invoice': 'purchase',
    'out_refund': 'sale',
    'in_refund': 'purchase',
}

# mapping invoice type to refund type
TYPE2REFUND = {
    'out_invoice': 'out_refund',        # Customer Invoice
    'in_invoice': 'in_refund',          # Vendor Bill
    'out_refund': 'out_invoice',        # Customer Refund
    'in_refund': 'in_invoice',          # Vendor Refund
}

MAGIC_COLUMNS = ('id', 'create_uid', 'create_date', 'write_uid', 'write_date')

class account_payment(osv.osv):
    _inherit = 'account.payment'

    currency_rate = fields.Float(string="Current Rate Rupee")
    v9_id = fields.Integer('Odoo9 Partner')

    # @api.onchange('journal_id')
    # def _onchange_journal(self):
    # 	if self.journal_id:
    # 		self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
    # 		# Set default payment method (we consider the first to be the default one)
    # 		payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
    # 		self.payment_method_id = payment_methods and payment_methods[0] or False
    # 		# Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
    # 		payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
    # 		return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
    # 	return {'domain': {'journal_id':[('company_id', '=', self.env.user.company_id.id),('type', 'in', ('bank', 'cash'))]}}

    def post(self):
        hasRateApplied = False
        if float(self.currency_rate) > 0:
            new_currency_rate_obj = 1 / float(self.currency_rate)
            currency = self.currency_id.with_context(date=self.payment_date or fields.Date.context_today(self))
            old_currency_rate_obj = currency.rate
            
            payment_date_with_time = datetime.strptime(self.payment_date, DEFAULT_SERVER_DATE_FORMAT)
            currencyRateObj=self.env['res.currency.rate'].search([('name','<=',payment_date_with_time.strftime(DEFAULT_SERVER_DATE_FORMAT)),('currency_id','=',currency.id)],order='id desc',limit=1)
            
            currencyRateObj.write({'rate': new_currency_rate_obj})
            hasRateApplied = True
        """ Create the journal items for the payment and update the payment's state to 'posted'.
        A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
        and another in the destination reconciliable account (see _compute_destination_account_id).
        If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
        If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:

            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)

            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()

            rec.state = 'posted'

            if hasRateApplied:
                currencyRateObj.write({'rate': old_currency_rate_obj})

class PaymentSwiftDetails(models.Model):
          
    _name='payment.swift.details'
    _order = "name"
    name = fields.Char(string='Our Correspondence Bank Name',translate=True, required=True)
    our_correspondence_bank_account_no = fields.Char(string='Our Correspondence Bank A/c no.')
    our_correspondence_bank_swift_code = fields.Char(string='Our Correspondence Bank Swift Code')
    routing_no = fields.Char('ABA FED Number')
    iban_no = fields.Char('IBAN No')
    bank_clearing_code = fields.Char("Bank Clearing Code")
    currency = fields.Many2one('res.currency',"Currency",domain=[('active', '=', True)],required=True)
    icici_bank_swift_code = fields.Char('ICICI BANK SWIFT CODE')

    brief_purpose = fields.Char('Brief Purpose')
    our = fields.Char('OUR')

    
    
        
    

class res_company(osv.osv):
    _name='res.company'
    _inherit='res.company'
    
    GST_No = fields.Char('GST No',tracking=True)
    pan_no = fields.Char('PAN No',tracking=True)
    code = fields.Char('Code',tracking=True)
    lut_number = fields.Char('LUT Number',tracking=True)    


