from credentials import odoo_9,odoo_15

#Invoice Payment Detail from Odoo9 to Odoo15

invoice_payment_field = ['name','company_id','currency_id','partner_id','payment_date','payment_method_id','journal_id','state','partner_type',
                         'amount','payment_type','currency_rate','payment_reference','move_line_ids','create_uid','write_uid']

invoice_payment_detail = odoo_9.execute('account.payment','search_read',[],invoice_payment_field)

count =0

for payment in invoice_payment_detail:
      
    payment_id = odoo_15.env['account.payment'].search([('name','=',payment['name'])])

    if not payment_id :
        
        odoo9_payment_id = odoo_9.env['account.payment'].browse(payment['id'])
        
        
        if odoo9_payment_id.currency_id:
            currency_id = odoo_15.env['res.currency'].search([('name','=',odoo9_payment_id.currency_id.name)])
        else:
            currency_id = []

        if odoo9_payment_id.partner_id:  
            partner_id = odoo_15.env['res.partner'].search([('name','=',odoo9_payment_id.partner_id.name)])
        else:
            partner_id = []


        if odoo9_payment_id.payment_method_id:
           payment_method_id = odoo_15.env['account.payment.method'].search([('payment_type','=',odoo9_payment_id.payment_method_id.payment_type)])
        else:
            payment_method_id = []
        #print(payment.get('move_line_ids'))
        if payment.get('move_line_ids'):
            move_line_p = odoo_9.env['account.move.line'].browse(payment.get('move_line_ids')[0])
            #print(move_line_p.move_id.id)
            move_id = odoo_15.env['account.move'].search([('v9_id','=',move_line_p.move_id.id)])
        else:
            move_id = []    
        if not move_id:
            continue
        invoice_payment_data = {
            'currency_id':currency_id[0] if currency_id else '',
            'partner_id':partner_id[0] if partner_id else '',
            'payment_method_id':payment_method_id[0] if payment_method_id else '',

            'partner_type':payment.get('partner_type'),
            'amount':payment.get('amount'),
            'payment_type':payment.get('payment_type'),
            'currency_rate':payment.get('currency_rate'),
            'payment_reference':payment.get('payment_reference'),
            'move_id':move_id[0] if move_id else '',
            'v9_id':payment['id']
            }

    
        v9_id = payment['id']
        
        print("""\ninsert into account_payment (currency_id,partner_id,
        payment_method_id,partner_type,amount
        ,payment_type,currency_rate,payment_reference,
        move_id,v9_id) values(""",invoice_payment_data['currency_id'],""",""",invoice_payment_data['partner_id'],""",""",
        invoice_payment_data['payment_method_id'],""",'""",invoice_payment_data['partner_type'],"""',""",
        invoice_payment_data['amount'],""",'""",invoice_payment_data['payment_type'],"""',""",
        invoice_payment_data['currency_rate'],""",'""",invoice_payment_data['payment_reference'],
              """',""",invoice_payment_data['move_id'],""",""",v9_id,""");""",sep="")