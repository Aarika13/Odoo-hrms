from odoo import api, fields, models, _



from odoo.addons.account.models.account_move import AccountMoveLine as InheritedAccountMoveLine

@api.model
def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
    res = {}

    # Compute 'price_subtotal'.
    line_discount_price_unit = price_unit * (1 - (discount / 100.0))
    subtotal = quantity * line_discount_price_unit
    # Compute 'price_total'.
    if taxes:
        taxes_res = taxes._origin.with_context(force_sign=1).compute_all(line_discount_price_unit,
            quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
        res['price_subtotal'] = taxes_res['total_excluded']
        res['price_total'] = taxes_res['total_included']
        res['price_total_without_tax_dis'] = quantity * price_unit
    else:
        res['price_total'] = res['price_subtotal'] = subtotal
        res['price_total_without_tax_dis'] = quantity * price_unit
    #In case of multi currency, round before it's use for computing debit credit
    if currency:
        res = {k: currency.round(v) for k, v in res.items()}
    return res


InheritedAccountMoveLine._get_price_total_and_subtotal_model = _get_price_total_and_subtotal_model
class AccountInvoiceLine(models.Model):
    _inherit='account.move.line'
 	
    # discount_amount = fields.Float(string='Discount')
    product_id = fields.Many2one('product.product', string='Product',ondelete='restrict', index=True)
    original_amount = fields.Monetary(compute='_compute_original_amount_of_product',readonly=True,string='Amount',store=True)
    product_hsn_or_sac_code = fields.Char("HSN/SAC" , related="product_id.l10n_in_hsn_code")
    v9_id = fields.Integer('Odoo9 Move Line')
    v9_invoice_id = fields.Integer('Odoo9 Invoice Line')
    price_total_without_tax_dis = fields.Monetary(string='Total', store=True, readonly=True,
        currency_field='currency_id')
    
    # @api.one
    # @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
    #     'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id')
    # def _compute_price(self):
    #     currency = self.invoice_id and self.invoice_id.currency_id or None
    #     price = self.price_unit * (1 - (0.0) / 100.0)
    #     taxes = False
    #     if self.invoice_line_tax_ids:
    #         taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
    #     self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
    #     self.price_subtotal -= self.discount_amount
    #     print "====================================="
    #     print self.price_subtotal
    #     if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
    #         price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
    #     sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
    #     self.price_subtotal_signed = price_subtotal_signed * sign

    @api.depends('price_unit','quantity')
    def _compute_original_amount_of_product(self):
        for record in self:
            if record.price_unit and record.quantity:
                record.original_amount = record.price_unit * record.quantity
            else:
                record.original_amount = 0
	            
