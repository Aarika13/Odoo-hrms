from credentials import odoo_9,odoo_15

#Invoice Payment Detail from Odoo9 to Odoo15

move_field = ['id','name','company_id','currency_id','partner_id','payment_date','payment_method_id','journal_id','state','partner_type',
                         'amount','payment_type','currency_rate','payment_reference','move_line_ids','create_uid','write_uid']

move_detail = odoo_9.execute('account.move','search_read',[],move_field)

count =0

for move in move_detail:
      
    move15 = odoo_15.env['account.move'].search([('v9_id','=',move['id'])])
    #print(move, move['id'],move15)
    if not move15:
        odoo9_move = odoo_9.env['account.move'].browse(move['id'])
        if  odoo9_move.partner_id :
            #print(odoo9_move)
            if odoo9_move.journal_id.name:
                odoo_15_journal = odoo_15.env['account.journal'].search([('name','=',odoo9_move.journal_id.name)])
            else:
                odoo_15_journal = []
            
            if odoo9_move.company_id.name:
                odoo_15_company = odoo_15.env['res.company'].search([('name','=',odoo9_move.company_id.name)])
            else:
                odoo_15_company = []
                
            if odoo9_move.currency_id.name:
                odoo_15_currency = odoo_15.env['res.currency'].search([('name','=',odoo9_move.currency_id.name)])
            else:
                odoo_15_currency = []

            if odoo9_move.partner_id.name:
                odoo_15_partner = odoo_15.env['res.partner'].search([('name','=',odoo9_move.partner_id.name)])
            else:
                odoo_15_partner = []
                
            if odoo9_move.partner_id.name:
                odoo_15_commercial_partner = odoo_15.env['res.partner'].search([('name','=',odoo9_move.partner_id.name)])
            else:
                odoo_15_commercial_partner = []
                

            odoo_15_partner_bank = []
            #print(odoo9_move.create_uid.name)    
            if odoo9_move:
                odoo_15_invoice_user = odoo_15.env['res.users'].search([('name','=',odoo9_move.create_uid.name)])
            else:
                odoo_15_invoice_user = []
                
            odoo_15_invoice_payment_term = []
            #print(odoo9_move.id)
            #print(odoo_15_partner[0])
            if odoo_15_partner :
                partner = odoo_15.env['res.partner'].browse(odoo_15_partner[0])
                invoice_partner_display_name = partner.name
            else:
                invoice_partner_display_name = 'null'
            
            odoo_15_payment_swift_id = []
                
            
            name = odoo9_move.ref if odoo9_move.ref else ''
            date = str(odoo9_move.date) 
            state = odoo9_move.state
            create_date = odoo9_move.create_date
            write_date = odoo9_move.write_date
                
            move_type = 'entry'
            journal_id = odoo_15_journal[0] if odoo_15_journal else ''
            company_id = odoo_15_company[0] if odoo_15_company else ''
            currency_id = odoo_15_currency[0] if odoo_15_currency else ''
            partner_id = odoo_15_partner[0] if odoo_15_partner else company_id
            commercial_partner_id = odoo_15_commercial_partner[0] if odoo_15_commercial_partner else 'null'
            is_move_sent = 'null'
            partner_bank_id = """,""" + str(odoo_15_partner_bank[0]) + """,""" if odoo_15_partner_bank else """null"""
            amount_untaxed = 0
            amount_tax = 0
            amount_total = odoo9_move.amount
            amount_residual =0
            amount_untaxed_signed = 0
            amount_tax_signed = 0
            amount_total_signed = odoo9_move.amount
            amount_total_in_currency_signed = odoo9_move.amount
            amount_residual_signed = 0
            payment_state = odoo9_move.state
            invoice_user_id = odoo_15_invoice_user[0] if odoo_15_invoice_user else ''
            invoice_date = "null"
            invoice_date_due =  "null"
            invoice_origin = 'null'
            invoice_payment_term_id = odoo_15_invoice_payment_term[0] if odoo_15_invoice_payment_term else 'null'
            
            
            create_uid = odoo_15_invoice_user[0] if odoo_15_invoice_user else ''
            write_uid = odoo_15_invoice_user[0] if odoo_15_invoice_user else ''
            partner_shipping_id = odoo_15_partner[0] if odoo_15_partner else 'null'
            payment_swift_id =  """null"""
            date_format = """null"""
            discount_type = """null"""
            discount_rate = """null"""
            amount_discount = 0
            v9_id = odoo9_move.id
            
            print("""\ninsert into account_move (name,date,state,move_type,journal_id,company_id,currency_id,partner_id,
                    commercial_partner_id,is_move_sent,partner_bank_id,amount_untaxed,amount_tax,amount_total,amount_residual,amount_untaxed_signed,
                    amount_tax_signed,amount_total_signed,amount_residual_signed,payment_state,invoice_user_id,invoice_date,invoice_date_due,
                    invoice_origin,invoice_payment_term_id,invoice_partner_display_name,create_uid,create_date,write_uid,write_date,
                    partner_shipping_id,payment_swift_id,date_format,discount_type,discount_rate,amount_discount,v9_id) values('""",name,"""','""",date,"""','""",
                    state,"""','""",move_type,"""',""",journal_id,""",""",company_id,""",""",currency_id,""",""",partner_id,""",""",commercial_partner_id,""",""",
                    is_move_sent,""",""",partner_bank_id,""",""",amount_untaxed,""",""",amount_tax,""",""",amount_total,""",""",
                    amount_residual,""",""",amount_untaxed_signed,""",""",amount_tax_signed,""",""",amount_total_signed,""",""",amount_residual_signed,
                    """,'""",payment_state,"""',""",invoice_user_id,""",""",invoice_date,""",""",invoice_date_due,""",""", invoice_origin,""",""",invoice_payment_term_id,""",""",invoice_partner_display_name,""",""",create_uid,""",'""",
                    create_date,"""',""",write_uid,""",'""",write_date,"""',""",partner_shipping_id,""",""",payment_swift_id,""",""",date_format,""",""",
                    discount_type,""",""",discount_rate,""",""",amount_discount,""",""",v9_id,""");""",sep="")