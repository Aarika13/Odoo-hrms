from credentials import odoo_9,odoo_15

invoice = ['id']
invoice_detail = odoo_9.execute('account.invoice','search_read',[],invoice)

for invoice in invoice_detail:
    
    odoo9_invoice = odoo_9.env['account.invoice'].browse(invoice['id'])
    #print(invoice['id'])
    move_id = odoo_9.env['account.move'].search([('id','=',odoo9_invoice.move_id.id)])

    if not move_id:
        print(invoice['id'])
        odoo9_invoice = odoo_9.env['account.invoice'].browse(invoice['id'])

        odoo9_account_invoice_line_data = odoo_9.env['account.invoice.line'].search([('invoice_id','=',invoice['id'])])

        price_unit_all = 0.0
        price_subtotal_all = 0.0
        price_total_all = 0.0
        discount_all = 0.0
        debit_all = 0.0
        credit_all = 0.0
        odoo_15_journal_id = []
        odoo_15_company_id = []
        odoo_15_company_currency_id = []
        odoo_15_currency_id = []
        odoo_15_partner_id = []
        odoo_15_move_id = []
        quantity = 0.0
        price_subtotal_signed = 0.0
        total_balance = 0.0
        total_price_subtotal = 0.0

        for odoo9_account_invoice_line in odoo9_account_invoice_line_data:
            odoo9_account_invoice_line = odoo_9.env['account.invoice.line'].browse(odoo9_account_invoice_line)

            odoo_15_move_id = 'null'
            odoo_15_move_id_name = 'null'
            
            

            if odoo9_invoice.journal_id.name:
                odoo_15_journal_id  = odoo_15.env['account.journal'].search([('name','=',odoo9_invoice.journal_id.name)])
            else:
                odoo_15_journal_id = []

            
            if odoo9_account_invoice_line.company_id.name:
                odoo_15_company_id = odoo_15.env['res.company'].search([('name','=',odoo9_account_invoice_line.company_id.name)])
            else:
                odoo_15_company_id= []

                
            if odoo9_account_invoice_line.company_id.currency:
                odoo_15_company_currency_id = odoo_15.env['res.currency'].search([('name','=',odoo9_account_invoice_line.company_id.currency_id.name)])
            else:
                odoo_15_company_currency_id = []     
    
            if odoo9_account_invoice_line.account_id:
                odoo_15_account_id = odoo_15.env['account.account'].search([('name','=',odoo9_account_invoice_line.account_id.name),('code','=',odoo9_account_invoice_line.account_id.code)])
            else:
                odoo_15_account_id = []

              

            if odoo9_account_invoice_line.currency_id:
                odoo_15_currency_id = odoo_15.env['res.currency'].search([('name','=',odoo9_account_invoice_line.currency_id.name)])
            else:
                odoo_15_currency_id = []

           

            if odoo9_account_invoice_line.partner_id.name:  
                odoo_15_partner_id = odoo_15.env['res.partner'].search([('name','=',odoo9_account_invoice_line.partner_id.name)])
            else:
                odoo_15_partner_id = []

                 
    
            if odoo9_account_invoice_line.uom_id:  
                odoo_15_product_uom_id= odoo_15.env['uom.uom'].search([('name','ilike',(odoo9_account_invoice_line.uom_id.name).split('(')[0])])
            else:
                odoo_15_product_uom_id = []

            
            
            if odoo9_account_invoice_line.product_id:  
                odoo_15_product_id= odoo_15.env['product.product'].search([('name','=',odoo9_account_invoice_line.product_id.name)])
            else:
                odoo_15_product_id = []

            

            if odoo9_account_invoice_line.account_analytic_id:
                odoo_15_analytic_account_id= odoo_15.env['account.analytic.account'].search([('name','=',odoo9_account_invoice_line.account_analytic_id.name)])
            else:
                odoo_15_analytic_account_id = []


            price_unit = odoo9_account_invoice_line.price_unit
            price_unit_all += price_unit
            price_subtotal = odoo9_account_invoice_line.price_subtotal
            price_subtotal_all += price_subtotal
            price_total = odoo9_account_invoice_line.price_subtotal
            price_total_all += price_total
            discount = odoo9_account_invoice_line.discount
            discount_all = discount


            move_id = odoo_15_move_id[0] if odoo_15_move_id else 'null'
            move_name = odoo_15_move_id_name
            date = odoo9_invoice.date_invoice
            ref = odoo9_invoice.draft_sequence
            parent_state = odoo9_invoice.state
            journal_id = odoo_15_journal_id[0] if odoo_15_journal_id else 'null'
            company_id = odoo_15_company_id[0] if odoo_15_company_id else 'null'
            company_currency_id = odoo_15_company_currency_id[0] if odoo_15_company_currency_id else 'null'
            account_id = odoo_15_account_id[0] if odoo_15_account_id else 'null'
            name = odoo9_account_invoice_line.name
            quantity = odoo9_account_invoice_line.quantity
            debit = 0.0
            price_subtotal_signed += odoo9_account_invoice_line.price_subtotal_signed 

            credit = odoo9_account_invoice_line.price_subtotal_signed

            balance = (odoo9_account_invoice_line.price_subtotal_signed) * (-1)
            total_balance += odoo9_account_invoice_line.price_subtotal_signed

            amount_currency = (odoo9_account_invoice_line.price_subtotal) * (-1)
            total_price_subtotal +=odoo9_account_invoice_line.price_subtotal
            
            currency_id = odoo_15_currency_id[0] if odoo_15_currency_id else '21'
            partner_id = odoo_15_partner_id[0] if odoo_15_partner_id else 'null'
            product_uom_id = """,""" + str(odoo_15_product_uom_id[0]) + ""","""  if odoo_15_product_uom_id else ",null,"
            product_id  = str(odoo_15_product_id[0]) + """,""" if odoo_15_product_id else "null,"
            amount_residual = 0.0
            amount_residual_currency = 0.0
            analytic_account_id = odoo_15_analytic_account_id[0] if odoo_15_analytic_account_id else ",null,"
            v9_invoice_id = odoo9_account_invoice_line.id

            print("""\ninsert into account_move_line (move_id,move_name,date,ref,parent_state,
            journal_id,company_id,company_currency_id,account_id,name
            ,quantity,debit,credit,balance,amount_currency,
            currency_id,partner_id,product_uom_id,
            product_id,amount_residual,amount_residual_currency,analytic_account_id,price_unit,price_subtotal,price_total,
            price_total_without_tax_dis,discount,v9_invoice_id) values(""",move_id,""",'""",move_name,"""','""",
            date,"""','""",ref,"""','""",parent_state,"""',""",journal_id,""",""",company_id,""",""",company_currency_id,""",""",account_id,""",'""",
            name,"""',""",quantity,""",""",debit,""",""",credit,""",""",balance,""",""",
            amount_currency,""",""",currency_id,""",""",partner_id,product_uom_id,product_id
            ,amount_residual,""",""",amount_residual_currency,analytic_account_id,
            price_unit,""",""",price_subtotal,""",""",price_total,""",""",price_total,""",""",discount,""",""",v9_invoice_id,""");""",sep="")


        parent_state = odoo9_invoice.state
        date = odoo9_invoice.date_invoice
        ref = odoo9_invoice.draft_sequence
        move_name = odoo_15_move_id_name
        odoo_15_account_id = odoo_15.env['account.account'].search([('name','=','Debtors')])
        account_id = odoo_15_account_id[0]
        name = '/'
        product_uom_id = ",null,"
        product_id = "null,"
        analytic_account_id =",null,"
        debit = price_subtotal_signed
        credit = 0.0
        balance = total_balance
        amount_currency = total_price_subtotal
        amount_residual = price_subtotal_signed
        amount_residual_currency = total_price_subtotal
        price_unit = price_unit_all * (-1)
        price_subtotal = price_subtotal_all * (-1)
        price_total = price_total_all * (-1)

        print("""\ninsert into account_move_line (move_id,move_name,date,ref,parent_state,
            journal_id,company_id,company_currency_id,account_id,name
            ,quantity,debit,credit,balance,amount_currency,
            currency_id,partner_id,product_uom_id,
            product_id,amount_residual,amount_residual_currency,analytic_account_id,price_unit,price_subtotal,price_total,
            price_total_without_tax_dis,discount,exclude_from_invoice_tab) values(""",move_id,""",'""",move_name,"""','""",
            date,"""','""",ref,"""','""",parent_state,"""',""",journal_id,""",""",company_id,""",""",company_currency_id,""",""",account_id,""",'""",
            name,"""',""",quantity,""",""",debit,""",""",credit,""",""",balance,""",""",
            amount_currency,""",""",currency_id,""",""",partner_id,product_uom_id,product_id
            ,amount_residual,""",""",amount_residual_currency,analytic_account_id
           ,price_unit,""",""",price_subtotal,""",""",price_total,""",""",price_total,""",""",discount,""",'True');""",sep="")
                                                                    
