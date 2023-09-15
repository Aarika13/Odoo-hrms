from credentials import odoo_9,odoo_15

invoice = ['id']
invoice_detail = odoo_9.execute('account.invoice','search_read',[],invoice)

for invoice in invoice_detail:
    
    odoo9_invoice = odoo_9.env['account.invoice'].browse(invoice['id'])

    move_id = odoo_9.env['account.move'].search([('id','=',odoo9_invoice.move_id.id)])

    if not move_id:
        #odoo9_move = odoo_9.env['account.move'].browse(move_id[0])
    
        if odoo9_invoice.journal_id.name:
            odoo_15_journal = odoo_15.env['account.journal'].search([('name','=',odoo9_invoice.journal_id.name)])
        else:
            odoo_15_journal = []
        
        if odoo9_invoice.company_id.name:
            odoo_15_company = odoo_15.env['res.company'].search([('name','=',odoo9_invoice.company_id.name)])
        else:
            odoo_15_company = []
            
        if odoo9_invoice.currency_id.name:
            odoo_15_currency = odoo_15.env['res.currency'].search([('name','=',odoo9_invoice.currency_id.name)])
        else:
            odoo_15_currency = []

        if odoo9_invoice.partner_id.name:
            odoo_15_partner = odoo_15.env['res.partner'].search([('name','=',odoo9_invoice.partner_id.name)])
        else:
            odoo_15_partner = []
            
        if odoo9_invoice.commercial_partner_id.name:
            odoo_15_commercial_partner = odoo_15.env['res.partner'].search([('name','=',odoo9_invoice.commercial_partner_id.name)])
        else:
            odoo_15_commercial_partner = []
            
        if odoo9_invoice.partner_bank_id.acc_number:
            odoo_15_partner_bank = odoo_15.env['res.partner.bank'].search([('acc_number','=',odoo9_invoice.partner_bank_id.acc_number)])
        else:
            odoo_15_partner_bank = []
            
        if odoo9_invoice.user_id.name:
            odoo_15_invoice_user = odoo_15.env['res.users'].search([('name','=',odoo9_invoice.user_id.name)])
        else:
            odoo_15_invoice_user = []
            
        if odoo9_invoice.payment_term_id.name:
            odoo_15_invoice_payment_term = odoo_15.env['account.payment.term'].search([('name','=',odoo9_invoice.payment_term_id.name)])
        else:
            odoo_15_invoice_payment_term = []
            
        invoice_partner_display_id = odoo_15.env['res.partner'].browse(odoo_15_partner[0])
        
        if odoo9_invoice.payment_swift_id.name:
            odoo_15_payment_swift_id = odoo_15.env['payment.swift.details'].search([('name','=',odoo9_invoice.payment_swift_id.name)])
        else:
            odoo_15_payment_swift_id = []
            
        
        name = odoo9_invoice.draft_sequence if odoo9_invoice.draft_sequence else ''
        date = str(odoo9_invoice.date_invoice)
        state = odoo9_invoice.state
        #name = odoo9_invoice.reference
        create_date = odoo9_invoice.create_date
        write_date = odoo9_invoice.write_date
        
            
        move_type = odoo9_invoice.type
        journal_id = odoo_15_journal[0] if odoo_15_journal else ''
        company_id = odoo_15_company[0] if odoo_15_company else ''
        currency_id = odoo_15_currency[0] if odoo_15_currency else ''
        partner_id = odoo_15_partner[0] if odoo_15_partner else ''
        commercial_partner_id = odoo_15_commercial_partner[0] if odoo_15_commercial_partner else ''
        is_move_sent = odoo9_invoice.sent
        partner_bank_id = """',""" + str(odoo_15_partner_bank[0]) + """,""" if odoo_15_partner_bank else """',null,"""
        amount_untaxed = odoo9_invoice.amount_untaxed
        amount_tax = odoo9_invoice.amount_tax
        amount_total = odoo9_invoice.amount_total
        amount_residual = odoo9_invoice.residual
        amount_untaxed_signed = odoo9_invoice.amount_untaxed_signed
        amount_tax_signed = 00
        amount_total_signed = odoo9_invoice.amount_total_signed
        amount_residual_signed = odoo9_invoice.residual_signed
        payment_state = odoo9_invoice.state
        invoice_user_id = odoo_15_invoice_user[0] if odoo_15_invoice_user else 'null'
        invoice_date = odoo9_invoice.date_invoice
        invoice_date_due = "','" + str(odoo9_invoice.date_due) + "','" if odoo9_invoice.date_due else "',null,'"
        invoice_origin = odoo9_invoice.origin
        invoice_payment_term_id = odoo_15_invoice_payment_term[0] if odoo_15_invoice_payment_term else 'null'
        invoice_partner_display_name = invoice_partner_display_id.name
        create_uid = odoo_15_invoice_user[0] if odoo_15_invoice_user else '399'
        write_uid = odoo_15_invoice_user[0] if odoo_15_invoice_user else '399'
        partner_shipping_id = odoo_15_partner[0] if odoo_15_partner else ''
        payment_swift_id =""",""" + str(odoo_15_payment_swift_id[0]) +""",'""" if odoo_15_payment_swift_id else """,null,'"""
        date_format = odoo9_invoice.date_format
        discount_type = odoo9_invoice.discount_type
        discount_rate = odoo9_invoice.discount_rate
        amount_discount = odoo9_invoice.amount_discount
        v9_invoice_id = odoo9_invoice.id
        #print("odoo9_move == ",odoo9_move)
        print("""\ninsert into account_move (name,date,state,move_type,journal_id,company_id,currency_id,partner_id,
                commercial_partner_id,is_move_sent,partner_bank_id,amount_untaxed,amount_tax,amount_total,amount_residual,amount_untaxed_signed,
                amount_tax_signed,amount_total_signed,amount_residual_signed,payment_state,invoice_user_id,invoice_date,invoice_date_due,
                invoice_origin,invoice_payment_term_id,invoice_partner_display_name,create_uid,create_date,write_uid,write_date,
                partner_shipping_id,payment_swift_id,date_format,discount_type,discount_rate,amount_discount,v9_invoice_id) values('""",name,"""','""",date,"""','""",
                state,"""','""",move_type,"""',""",journal_id,""",""",company_id,""",""",currency_id,""",""",partner_id,""",""",commercial_partner_id,""",'""",
                is_move_sent,partner_bank_id,amount_untaxed,""",""",amount_tax,""",""",amount_total,""",""",
                amount_residual,""",""",amount_untaxed_signed,""",""",amount_tax_signed,""",""",amount_total_signed,""",""",amount_residual_signed,
                """,'""",payment_state,"""',""",invoice_user_id,""",'""",invoice_date,invoice_date_due,
                invoice_origin,"""',""",invoice_payment_term_id,""",'""",invoice_partner_display_name,"""',""",create_uid,""",'""",
                create_date,"""',""",write_uid,""",'""",write_date,"""',""",partner_shipping_id,payment_swift_id,date_format,"""','""",
                discount_type,"""',""",discount_rate,""",""",amount_discount,""",""",v9_invoice_id,""");""",sep="")



#after importing invoice for move change condition of (if move_id:) to if (not move_id:) for draft invoice (line no 19)