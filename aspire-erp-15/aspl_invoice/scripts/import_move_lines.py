from credentials import odoo_9,odoo_15

#account_analytic_account detail

analytic_acccount_field = ['name','company_id','partner_id']

analytic_acccount_detail = odoo_9.execute('account.analytic.account','search_read',[],analytic_acccount_field)

for analytic_acccount in analytic_acccount_detail:
    
    analytic_acccount_id = odoo_15.env['account.analytic.account'].search([('name','=',analytic_acccount['name'])])

    if not analytic_acccount_id:

        if analytic_acccount['company_id']:
            company_id = odoo_15.env['res.company'].search([('name','=',analytic_acccount['company_id'][1])])
        else:
            company_id = []

        if analytic_acccount['partner_id']:
            partner_id = odoo_15.env['res.partner'].search([('name','=',analytic_acccount['partner_id'][1])])
        else:
            partner_id = []

        analytic_acccount_data = {
            'name':analytic_acccount.get('name'),
            'company_id':company_id[0] if company_id else '',
            'partner_id':partner_id[0] if partner_id else '',
            }
        
        v_15_attachment_id = odoo_15.execute('account.analytic.account', 'create', analytic_acccount_data)




#account_move_line detail

account_move_line = ['id']
account_move_line_detail = odoo_9.execute('account.move.line','search_read',[],account_move_line)

count =0
for account_move_line in account_move_line_detail:
    #print(account_move_line['id'])
    odoo9_account_move_line = odoo_9.env['account.move.line'].browse(account_move_line['id'])
    #print(odoo9_account_move_line)
    #odoo_15_move_id = odoo_15.env['account.move'].search([('v9_id','=',odoo9_account_move_line.invoice_id.id)])
    
    if odoo9_account_move_line.move_id:
        #print(odoo9_account_move_line.move_id.id)
        odoo_15_move_id = odoo_15.env['account.move'].search([('v9_id','=',odoo9_account_move_line.move_id.id)])
    else:
        find_move = odoo9_account_move_line.move_id.ref
        odoo_15_move_id = odoo_15.env['account.move'].search([('name','=',find_move)])
    #print(odoo_15_move_id)
    odoo_15_move_id_data = odoo_15.env['account.move'].browse(odoo_15_move_id[0])
    

    if odoo9_account_move_line.journal_id.name:
        odoo_15_journal_id = odoo_15.env['account.journal'].search([('name','=',odoo9_account_move_line.journal_id.name)])
    else:
        odoo_15_journal_id = []

    if odoo9_account_move_line.company_id.name:
        odoo_15_company_id = odoo_15.env['res.company'].search([('name','=',odoo9_account_move_line.company_id.name)])
    else:
        odoo_15_company_id= []

        
    if odoo9_account_move_line.company_currency_id.name:
        odoo_15_company_currency_id = odoo_15.env['res.currency'].search([('name','=',odoo9_account_move_line.company_currency_id.name)])
    else:
        odoo_15_company_currency_id = []
        

    if odoo9_account_move_line.account_id:
        odoo_15_account_id = odoo_15.env['account.account'].search([('name','=',odoo9_account_move_line.account_id.name),('code','=',odoo9_account_move_line.account_id.code)])
    else:
        odoo_15_account_id = []

    if odoo9_account_move_line.currency_id:
        odoo_15_currency_id = odoo_15.env['res.currency'].search([('name','=',odoo9_account_move_line.currency_id.name)])
    else:
        odoo_15_currency_id = []


    if odoo9_account_move_line.partner_id.name:  
        odoo_15_partner_id = odoo_15.env['res.partner'].search([('name','=',odoo9_account_move_line.partner_id.name)])
    else:
        odoo_15_partner_id = []    


    if odoo9_account_move_line.product_uom_id:  
        odoo_15_product_uom_id= odoo_15.env['uom.uom'].search([('name','ilike',(odoo9_account_move_line.product_uom_id.name).split('(')[0])])
    else:
        odoo_15_product_uom_id = []


    
    if odoo9_account_move_line.product_id:  
        odoo_15_product_id= odoo_15.env['product.product'].search([('name','=',odoo9_account_move_line.product_id.name)])
    else:
        odoo_15_product_id = []

    if odoo9_account_move_line.analytic_account_id:
        odoo_15_analytic_account_id= odoo_15.env['account.analytic.account'].search([('name','=',odoo9_account_move_line.analytic_account_id.name)])
    else:
        odoo_15_analytic_account_id = []

    odoo9_invoice_line = odoo9_account_move_line.invoice_id
    #print(odoo9_account_move_line)
    #print(odoo_15_product_id,odoo9_account_move_line.quantity,odoo9_invoice_line.id,odoo9_account_move_line.product_id.id)
    if odoo_15_product_id:
        odoo9_account_invoice_line = odoo_9.env['account.invoice.line'].search([('invoice_id','=',odoo9_invoice_line.id),('product_id','=',odoo9_account_move_line.product_id.id)])
        for line in odoo9_account_invoice_line:
            odoo9_account_invoice_line_obj = odoo_9.env['account.invoice.line'].browse(line)
            if odoo9_account_invoice_line_obj.quantity - odoo9_account_move_line.quantity < 0.01:
                #print(odoo9_account_invoice_line)
                #odoo9_account_invoice_line_obj = odoo_9.env['account.invoice.line'].browse(odoo9_account_invoice_line[0])

                price_unit = odoo9_account_invoice_line_obj.price_unit
                price_subtotal = odoo9_account_invoice_line_obj.price_subtotal
                price_total = odoo9_account_invoice_line_obj.price_subtotal
                discount = odoo9_account_invoice_line_obj.discount
    else:
        odoo9_account_invoice_line = odoo_9.env['account.invoice.line'].search([('invoice_id','=',odoo9_invoice_line.id)])
        price_unit = 0.0
        price_subtotal = 0.0
        price_total = 0.0
        discount = 0.0
        for invoice_line in odoo9_account_invoice_line:
            odoo9_account_invoice_line_obj = odoo_9.env['account.invoice.line'].browse(invoice_line)
            price_unit += (odoo9_account_invoice_line_obj.price_unit) * (-1)
            price_subtotal += (odoo9_account_invoice_line_obj.price_subtotal) * (-1)
            price_total += (odoo9_account_invoice_line_obj.price_subtotal) * (-1)
            discount = odoo9_account_invoice_line_obj.discount
    
    move_id = odoo_15_move_id[0] if odoo_15_move_id else ''
    move_name = odoo_15_move_id_data.name
    date = odoo9_account_move_line.date
    ref = odoo9_account_move_line.ref
    parent_state = odoo_15_move_id_data.state
    journal_id = odoo_15_journal_id[0] if odoo_15_journal_id else ''
    company_id = odoo_15_company_id[0] if odoo_15_company_id else ''
    company_currency_id = odoo_15_company_currency_id[0] if odoo_15_company_currency_id else ''
    account_id = odoo_15_account_id[0] if odoo_15_account_id else ''
    name = odoo9_account_move_line.name
    quantity = odoo9_account_move_line.quantity
    debit = odoo9_account_move_line.debit
    credit = odoo9_account_move_line.credit
    balance = odoo9_account_move_line.balance
    amount_currency = odoo9_account_move_line.amount_currency
    reconciled = odoo9_account_move_line.reconciled
    blocked = odoo9_account_move_line.blocked
    currency_id = odoo_15_currency_id[0] if odoo_15_currency_id else '21'
    partner_id = odoo_15_partner_id[0] if odoo_15_partner_id else 'null'
    product_uom_id = """,""" + str(odoo_15_product_uom_id[0]) + ""","""  if odoo_15_product_uom_id else ",null,"
    product_id  = str(odoo_15_product_id[0]) + """,""" if odoo_15_product_id else "null,"
    #payment_id ="','" + str(odoo9_invoice.date_due) + "','" if odoo9_invoice.date_due else "',null,'"
    amount_residual = odoo9_account_move_line.amount_residual
    amount_residual_currency = odoo9_account_move_line.amount_residual_currency
    analytic_account_id = odoo_15_analytic_account_id[0] if odoo_15_analytic_account_id else ",null,"
    v9_id = odoo9_account_move_line.id

    print("""\ninsert into account_move_line (move_id,move_name,date,ref,parent_state,
        journal_id,company_id,company_currency_id,account_id,name
        ,quantity,debit,credit,balance,amount_currency,
        reconciled,blocked,currency_id,partner_id,product_uom_id,
        product_id,amount_residual,amount_residual_currency,analytic_account_id,v9_id,price_unit,price_subtotal,price_total,price_total_without_tax_dis,discount) \n values(""",move_id,""",'""",move_name,"""','""",
        date,"""','""",ref,"""','""",parent_state,"""',""",journal_id,""",""",company_id,""",""",company_currency_id,""",""",account_id,""",'""",
        name,"""',""",quantity,""",""",debit,""",""",credit,""",""",balance,""",""",
        amount_currency,""",""",reconciled,""",""",blocked,""",""",currency_id,""",""",partner_id,product_uom_id,product_id
        ,amount_residual,""",""",amount_residual_currency,analytic_account_id,
        v9_id,""",""",price_unit,""",""",price_subtotal,""",""",price_total,""",""",price_total,""",""",discount,""");""",sep="")