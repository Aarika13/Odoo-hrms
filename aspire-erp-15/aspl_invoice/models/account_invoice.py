import json
from lxml import etree
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY
from odoo import api, fields, models, _
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang
import base64
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz
import odoo.addons.decimal_precision as dp
from collections import defaultdict
import re
import logging
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

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def name_get(self):
        res = []
        for journal in self:
            name = journal.name + ' - ' + journal.code
            if journal.currency_id and journal.currency_id != journal.company_id.currency_id:
                name = "%s (%s)" % (name,journal.currency_id.name)
            res += [(journal.id, name)]
        return res
    
# from odoo.addons.account.models.sequence_mixin import SequenceMixin as InheritedSequenceMixin
# _sequence_field = "reference"
# InheritedSequenceMixin._sequence_field = _sequence_field

from odoo.addons.account.models.account_move import AccountMove as InheritedAccountMove

def action_post(self):
        moves_with_payments = self.filtered('payment_id')
        other_moves = self - moves_with_payments
        if moves_with_payments:
            moves_with_payments.payment_id.action_post()
        if other_moves:
            other_moves._post(soft=False)

        if not self.move_type or self.move_type in ['in_invoice','in_refund']:
            pass
            # raise UserError(_('You can not generate invoice number for vendor bill.'))
        else:
            if not self.company_id.GST_No:
                raise UserError("Please set 'GST code' in the company.")
            else:
                if not self.invoice_date:
                    self.invoice_date = datetime.now().date()
                if not self.draft_sequence:
                    invoice_format = self.company_id.GST_No[0:2] + self.company_id.GST_No[-3::1] + self.get_financial_year(str(self.invoice_date)).zfill(4)
                    account_invoice_id = self.sudo().search([('draft_sequence', 'like', invoice_format)], order='invoice_number_sequence desc', limit=1)
                    if account_invoice_id:
                        self.draft_sequence =  self.company_id.GST_No[0:2] + self.company_id.GST_No[-3::1] + self.get_financial_year(str(self.invoice_date)) + str(account_invoice_id.invoice_number_sequence + 1 ).zfill(4) 
                        self.invoice_number_sequence = account_invoice_id.invoice_number_sequence + 1
                    else:
                        self.draft_sequence =  self.company_id.GST_No[0:2] + self.company_id.GST_No[-3::1] + self.get_financial_year(str(self.invoice_date)) + str(1).zfill(4)
                        self.invoice_number_sequence = 1
                    self.reference = self.draft_sequence
                    self.gst_invoice_date = datetime.now().date()
        return False

InheritedAccountMove.action_post = action_post
class AccountInvoice(models.Model):
    _inherit = 'account.move'

    # partner_id = fields.Many2one('res.partner', change_default=True,
    #     required=True, readonly=True, states={'draft': [('readonly', False)]},
    #     track_visibility='always')
    payment_swift_id = fields.Many2one('payment.swift.details',string='Correspondence Bank',states={'paid': [('readonly', True)]},domain="[('currency', '=', currency_id )]")
    draft_sequence = fields.Char('Invoice Number ',copy=False)
    gst_invoice_sequence = fields.Char('GST Invoice Number',copy=False)
    gst_invoice_date = fields.Date('GST Invoice Date ',copy=False)
    invoice_number_sequence = fields.Integer('Invoice Number Sequence')
    gst_invoice_number_sequence = fields.Integer('GST Invoice Number Sequence')
    check_gst_no = fields.Boolean(compute='_get_gst_no')
    this_year = fields.Boolean(compute='_is_this_year_invoice')
    # invoice_date = fields.Char('Invoice Date')
    date_due_as_on_draft = fields.Date('Due Date', help="This field is created as Odoo doesn't set due date when an invoice is in Draft stage.",copy=False)
    date_format = fields.Char('Date Format')
    v9_id = fields.Integer('Odoo9 Move')
    v9_invoice_id = fields.Integer('Odoo9 Invoice')
    # current_year = fields.Char("Current Year",store=True,compute='_check_current_year')
    # previous_year = fields.Char("Previous Year",store=True,compute='_check_previous_year')
    
    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], string='Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]}, default='percent')
    discount_rate = fields.Float('Discount Amount', digits=(16, 2), readonly=True, states={'draft': [('readonly', False)]})
    amount_discount = fields.Monetary(string='Discount', store=True, readonly=True, compute='_compute_amount')
    reference = fields.Char(string='Reference')
    
    # @api.depends("invoice_date")
    # def _check_current_year(self):
    #     print("called current year")
    #     invoice_date = self.invoice_date
    #     current_date = datetime.today().date()
    #     current_month = int(datetime.today().strftime('%m'))
    #     print("current_month == ",type(current_month))

    #     current_year = datetime.today().date()
    #     next_year = (current_date+timedelta(days=365))
    #     previous_year = (current_date-timedelta(days=365))

    #     if current_month<=3:
    #         sd = datetime.strftime(previous_year,'%Y-04-01')
    #         ed = datetime.strftime(current_year,'%Y-03-31')            
    #         startDateObj = datetime.strptime(sd, '%Y-%m-%d')
    #         endDateObj = datetime.strptime(ed, '%Y-%m-%d')
            
    #         print("invoice_date == ",invoice_date)
    #         for date in rrule(DAILY, dtstart=startDateObj, until=endDateObj):
    #             dt = datetime.strftime(date, '%Y-%m-%d')
    #             print("dt date == ",dt)
    #             if dt==invoice_date:
    #                 self.current_year = 1
    #                 print("connected === self.current_year == ",self.current_year)
    #                 break
    #             else:
    #                 self.current_year = 0
    #                 print("self.current_year == ",self.current_year)

    #     if current_month>3:
    #         sd = datetime.strftime(current_year,'%Y-04-01')
    #         ed = datetime.strftime(next_year,'%Y-03-31')            
    #         startDateObj = datetime.strptime(sd, '%Y-%m-%d')
    #         endDateObj = datetime.strptime(ed, '%Y-%m-%d')
            
    #         print("invoice_date == ",invoice_date)
    #         for date in rrule(DAILY, dtstart=startDateObj, until=endDateObj):
    #             dt = datetime.strftime(date, '%Y-%m-%d')
    #             print("dt date == ",dt)
    #             if dt==invoice_date:
    #                 self.current_year = 1
    #                 print("connected === self.current_year == ",self.current_year)
    #                 break
    #             else:
    #                 self.current_year = 0
    #                 print("self.current_year == ",self.current_year)

    # @api.depends("invoice_date")
    # def _check_previous_year(self):
    #     print("called current year")
    #     invoice_date = self.invoice_date
    #     current_date = datetime.today().date()
    #     current_month = int(datetime.today().strftime('%m'))
    #     print("previous current_month == ",current_month)

    #     current_year = datetime.today().date()
    #     previous_year = (current_date-timedelta(days=364))
    #     second_previous_year = (current_date-timedelta(days=729))

    #     if current_month <= 3:
    #         sd = datetime.strftime(second_previous_year,'%Y-04-01')
    #         ed = datetime.strftime(previous_year,'%Y-03-31')            
    #         startDateObj = datetime.strptime(sd, '%Y-%m-%d')
    #         endDateObj = datetime.strptime(ed, '%Y-%m-%d')
            
    #         for date in rrule(DAILY, dtstart=startDateObj, until=endDateObj):
    #             dt = datetime.strftime(date, '%Y-%m-%d')
    #             if dt==invoice_date:
    #                 self.previous_year = 1
    #                 break
    #             else:
    #                 self.previous_year = 0

    #     if current_month>3:
    #         sd = datetime.strftime(previous_year,'%Y-04-01')
    #         ed = datetime.strftime(current_year,'%Y-03-31')            
    #         startDateObj = datetime.strptime(sd, '%Y-%m-%d')
    #         endDateObj = datetime.strptime(ed, '%Y-%m-%d')
            
    #         for date in rrule(DAILY, dtstart=startDateObj, until=endDateObj):
    #             dt = datetime.strftime(date, '%Y-%m-%d')
    #             if dt==invoice_date:
    #                 self.previous_year = 1
    #                 break
    #             else:
    #                 self.previous_year = 0

    def _get_gst_no(self):
        for record in self:
            if record.company_id.GST_No and record.state != 'draft':
                record.check_gst_no = True
            else:
                record.check_gst_no = False
    def _is_this_year_invoice(self):
        fiscal_month = 4
        month = date.today().month
        now = datetime.now(pytz.timezone(self.env.context.get('tz') or 'UTC'))
        year=now.strftime('%Y')
        previousYear = (now - relativedelta(years=1)).strftime('%Y')
        nextYear = (now + relativedelta(years=1)).strftime('%Y')     

        for record in self:
            if month < fiscal_month  and int(month) >= 1 :
                BOP = date(int(previousYear),fiscal_month,1)
                EOP = date.today()
            else:
                BOP = date(int(year),fiscal_month,1)
                EOP = date.today()
        record.this_year= datetime.strptime(str(record.invoice_date), '%Y-%m-%d').date() >= BOP and datetime.strptime(str(record.invoice_date), '%Y-%m-%d').date() <= EOP
                
    # sub_total = fields.Float(compute='_compute_total_price_on_discount',string="Sub Total")

    # @api.onchange('payment_term_id')
    # def _onchange_payment_term_id(self):
    #     return {'domain': {'payment_term_id':[('company_id', '=', self.env.user.company_id.id)]}}



    @api.model
    def _prepare_refund(self, invoice, invoice_date=None, date=None, description=None, journal_id=None):
        
        """ Prepare the dict of values to create the new refund from the invoice.
            This method may be overridden to implement custom
            refund generation (making sure to call super() to establish
            a clean extension chain).

            :param record invoice: invoice to refund
            :param string invoice_date: refund creation date from the wizard
            :param integer date: force date from the wizard
            :param string description: description of the refund from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the refund
        """
        values = {}
        for field in ['name', 'reference', 'comment', 'date_due', 'partner_id', 'company_id',
                'account_id', 'currency_id', 'payment_term_id','payment_swift_id', 'user_id', 'fiscal_position_id']:
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._refund_cleanup_lines(invoice.invoice_line_ids)

        tax_lines = filter(lambda l: l.manual, invoice.tax_line_ids)
        values['tax_line_ids'] = self._refund_cleanup_lines(tax_lines)

        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['invoice_date'] = invoice_date or fields.Date.context_today(invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values

    def unlink(self):
        for invoice in self:
            if invoice.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an invoice which is not draft or cancelled. You should refund it instead.'))
            # elif invoice.move_name:
            #     raise UserError(_('You cannot delete an invoice after it has been validated (and received a number). You can set it back to "Draft" state and modify its content, then re-confirm it.'))

            if invoice.invoice_line_ids and invoice.state in ['draft']:#and not invoice.move_name
                activity = self.env['account.analytic.line'].search([('invoice_id','=',invoice.id)])
                if activity:
                    for record in activity:
                        record.write({'invoiced':False,'invoice_id':None})

        return super(AccountInvoice, self).unlink()

    @api.model
    def create(self, vals):
        # if not vals.get('account_id',False):
        #     raise UserError(_('Configuration error!\nCould not find any account to create the invoice, are you sure you have a chart of account installed?'))
        if 'date_format' not in vals:
            vals['date_format'] = '%B %d, %Y'

        invoiceDate = vals.get('invoice_date')
        paymentTermId = vals.get('payment_term_id')
        
        if invoiceDate and paymentTermId :
            vals['date_due_as_on_draft'] = self.calculateDueDate(paymentTermId,invoiceDate)

        # vals['draft_sequence']  = self.env['ir.sequence'].next_by_code('invoice.draft.sequence')
        return super(AccountInvoice, self.with_context(mail_create_nolog=True)).create(vals)

    def calculateDueDate(self,payment_term_id,invoice_date):
        _logger.info("Search for payment term line record to determine how many days needs to be added to calculate the due date.")

        paymentTermModel = self.env['account.payment.term']
        paymentTerm = paymentTermModel.search([('id','=',payment_term_id)])
        paymentTermLineModel = self.env['account.payment.term.line']
        paymentTermLines = paymentTermLineModel.search([('payment_id','=',
                                        paymentTerm.id),
                                        ('value','=','balance'),('option','=','day_after_invoice_date')])
        daysToAdd=0
        maxDate=datetime(1900, 1, 1)
        for line in paymentTermLines:
            if maxDate < datetime.strptime(str(line.write_date),DEFAULT_SERVER_DATETIME_FORMAT):
                maxDate = datetime.strptime(str(line.write_date),DEFAULT_SERVER_DATETIME_FORMAT)
                daysToAdd = line.days
        return datetime.strptime(str(invoice_date),DEFAULT_SERVER_DATE_FORMAT) + timedelta(days=daysToAdd)
    
    # @api.onchange('partner_id', 'company_id')
    # def _onchange_partner_id(self):
        
    #     account_id = False
    #     payment_term_id = False
    #     fiscal_position = False
    #     bank_id = False
    #     p = self.partner_id
    #     company_id = self.company_id.id
    #     type = self.type
    #     if p:
    #         partner_id = p.id
    #         rec_account = p.property_account_receivable_id
    #         pay_account = p.property_account_payable_id
    #         if company_id:
    #             if p.property_account_receivable_id.company_id and \
    #                     p.property_account_receivable_id.company_id.id != company_id and \
    #                     p.property_account_payable_id.company_id and \
    #                     p.property_account_payable_id.company_id.id != company_id:
    #                 prop = self.env['ir.property']
    #                 rec_dom = [('name', '=', 'property_account_receivable_id'), ('company_id', '=', company_id)]
    #                 pay_dom = [('name', '=', 'property_account_payable_id'), ('company_id', '=', company_id)]
    #                 res_dom = [('res_id', '=', 'res.partner,%s' % partner_id)]
    #                 rec_prop = prop.search(rec_dom + res_dom) or prop.search(rec_dom, limit=1)
    #                 pay_prop = prop.search(pay_dom + res_dom) or prop.search(pay_dom, limit=1)
    #                 rec_account = rec_prop.get_by_record(rec_prop)
    #                 pay_account = pay_prop.get_by_record(pay_prop)
    #                 if not rec_account and not pay_account:
    #                     action = self.env.ref('account.action_account_config')
    #                     msg = _('Cannot find a chart of accounts for this company, You should configure it. \nPlease go to Account Configuration.')
    #                     raise RedirectWarning(msg, action.id, _('Go to the configuration panel'))

    #         if type in ('out_invoice', 'out_refund'):
    #             account_id = rec_account.id
    #             payment_term_id = p.property_payment_term_id.id
    #             currency_id = p.currency.id
    #             company_id = p.company_id
    #             payment_swift_id = p.payment_detial.id
    #             user_id = p.user_id.id
    #         else:
    #             account_id = pay_account.id
    #             payment_term_id = p.property_supplier_payment_term_id.id
    #             payment_swift_id = p.payment_detial.id
    #             company_id = p.company_id
    #             currency_id = p.currency.id
    #             user_id = p.user_id.id
    #         addr = p.address_get(['delivery'])
    #         fiscal_position = self.env['account.fiscal.position'].get_fiscal_position(p.id, delivery_id=addr['delivery'])

    #     self.account_id = account_id
    #     self.payment_term_id = payment_term_id
    #     self.user_id = p.user_id.id
    #     self.fiscal_position_id = fiscal_position
    #     self.currency_id = p.currency.id
    #     self.payment_swift_id = p.payment_detial.id

    #     if type in ('in_invoice', 'out_refund'):
    #         bank_ids = p.commercial_partner_id.bank_ids
    #         bank_id = bank_ids[0].id if bank_ids else False
    #         self.partner_bank_id = bank_id
    #         return {'domain': {'partner_bank_id': [('id', 'in', bank_ids.ids)]}}
    #     return {}


    def invoice_validate(self):
        for invoice in self:
            self.ensure_one()
        
        
        #refuse to validate a vendor bill/refund if there already exists one with the same reference for the same partner,
        #because it's probably a double encoding of the same bill/refund
        if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
            if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference), ('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id)]):
                raise UserError(_("Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))
        self.generate_gst_invoice()
        self.generate_report_file()
        return self.write({'state': 'open'})

    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.invoice_date:
                inv.with_context(ctx).write({'invoice_date': fields.Date.context_today(self)})
            invoice_date = inv.invoice_date
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.compute(total, invoice_date)[0]
                res_amount_currency = total_currency
                ctx['date'] = invoice_date
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            if not self.draft_sequence:
                self.action_generate_invoice_number()
        
            date = inv.date or invoice_date
            reference = inv.reference

            if not inv.reference:
                    reference=inv.draft_sequence
            move_vals = {
                'ref': reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['dont_create_taxes'] = True
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            move.post()
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True




    def generate_gst_invoice(self):
        for invoice in self:
            if invoice.draft_sequence and invoice.company_id.GST_No:
                self.generate_gst_invoice_number()
                invoice.gst_invoice_date = datetime.now().date()
    
    def generate_report_file(self):
        # generate pdf and add to attachment
        for invoice in self:
            document = self.env['report'].sudo().get_pdf(invoice, 'invoice_aspire.print_time_and_material_invoice')
            versonNumber = self.get_invoice_version()
            self.env['ir.attachment'].create({
            'name': invoice.number + "-v" + str(versonNumber),
            'type': 'binary',
            'datas': base64.encodestring(document),
            'datas_fname': invoice.draft_sequence + "-v" + str(versonNumber)+ '.pdf',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'mimetype': 'application/x-pdf'})

    def get_invoice_version(self):
        attachmentData = self.env['ir.attachment'].search([('res_id', '=', self.id)])
        return len(attachmentData)+1



    def get_financial_year(self,datestring):
        date = datetime.strptime(datestring, "%Y-%m-%d").date()
        #initialize the current year
        year_of_date=date.year
        #initialize the current financial year start date
        financial_year_start_date = datetime.strptime(str(year_of_date)+"-04-01","%Y-%m-%d").date()
        if date<financial_year_start_date:
                return str(financial_year_start_date.year-1)+ str(financial_year_start_date.year)[2:]
        else:
                return str(financial_year_start_date.year)+ str(financial_year_start_date.year+1)[2:] 



    def generate_gst_invoice_number(self):
        gst_invoice_format = str(self.company_id.GST_No[:2]) + str(self.company_id.GST_No[-3:]) + self.get_financial_year(str(datetime.now().date())).zfill(4)

        account_invoice_id = self.sudo().search([('gst_invoice_sequence', 'like', gst_invoice_format)], order='gst_invoice_number_sequence desc', limit=1)
        if account_invoice_id:
            self.gst_invoice_sequence =  str(self.company_id.GST_No[:2]) + str(self.company_id.GST_No[-3:]) + self.get_financial_year(str(datetime.now().date())) + str(account_invoice_id.gst_invoice_number_sequence + 1 ).zfill(4)
            self.gst_invoice_number_sequence = account_invoice_id.gst_invoice_number_sequence + 1
        else:
            self.gst_invoice_sequence =  str(self.company_id.GST_No[:2]) + str(self.company_id.GST_No[-3:]) + self.get_financial_year(str(datetime.now().date())) + str(1).zfill(4)
            self.gst_invoice_number_sequence = 1
                    
    def action_generate_invoice_number(self):

        def journal_key(move):
            return (move.journal_id, move.journal_id.refund_sequence and move.move_type)

        def date_key(move):
            return (move.date.year, move.date.month)

        grouped = defaultdict(  # key: journal_id, move_type
            lambda: defaultdict(  # key: first adjacent (date.year, date.month)
                lambda: {
                    'records': self.env['account.move'],
                    'format': False,
                    'format_values': False,
                    'reset': False
                }
            )
        )
        self = self.sorted(lambda m: (m.date, m.ref or '', m.id))
        highest_name = self[0]._get_last_sequence() if self else False

        # Group the moves by journal and month
        for move in self:
            if not highest_name and move == self[0] and not move.posted_before and move.date:
                # In the form view, we need to compute a default sequence so that the user can edit
                # it. We only check the first move as an approximation (enough for new in form view)
                pass

            group = grouped[journal_key(move)][date_key(move)]
            
            if not group['records']:
                # Compute all the values needed to sequence this whole group
                move._set_next_sequence()
                group['format'], group['format_values'] = move._get_sequence_format_param(move.name)
                group['reset'] = move._deduce_sequence_number_reset(move.name)
            group['records'] += move

        final_batches = []
        for journal_group in grouped.values():
            journal_group_changed = True
            for date_group in journal_group.values():
                if (
                    journal_group_changed
                    or final_batches[-1]['format'] != date_group['format']
                    or dict(final_batches[-1]['format_values'], seq=0) != dict(date_group['format_values'], seq=0)
                ):
                    final_batches += [date_group]
                    journal_group_changed = False
                elif date_group['reset'] == 'never':
                    final_batches[-1]['records'] += date_group['records']
                elif (
                    date_group['reset'] == 'year'
                    and final_batches[-1]['records'][0].date.year == date_group['records'][0].date.year
                ):
                    final_batches[-1]['records'] += date_group['records']
                else:
                    final_batches += [date_group]

        # Give the name based on previously computed values
        for batch in final_batches:
            for move in batch['records']:
                move.name = batch['format'].format(**batch['format_values'])
                batch['format_values']['seq'] += 1
            batch['records']._compute_split_sequence()

            self.filtered(lambda m: not m.name).name = '/'
            self.invoice_date = datetime.now().date()
