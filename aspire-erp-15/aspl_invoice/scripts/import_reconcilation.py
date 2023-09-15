from credentials import odoo_9,odoo_15

#Invoice Payment Detail from Odoo9 to Odoo15

partial_reconsile_field = ['credit_move_id','debit_move_id','full_reconsile_id','currency_id','amount','amount_currency','company_id']

partial_reconsile_detail = odoo_9.execute('account.partial.reconcile','search_read',[],partial_reconsile_field)
count =0
for reconsile in partial_reconsile_detail:

        #if count == 0 and reconsile['id'] == 6 :
            reconsile_id = odoo_9.env['account.partial.reconcile'].browse(reconsile['id'])
            #print(reconsile['id'])
            credit_move_id = odoo_15.env['account.move.line'].search([('v9_id','=',reconsile_id.credit_move_id.id)])
            credit_move_id = credit_move_id[0] if credit_move_id else 'null'
            debit_move_id = odoo_15.env['account.move.line'].search([('v9_id','=',reconsile_id.debit_move_id.id)])
            debit_move_id = debit_move_id[0] if debit_move_id else 'null'
            debit_currency_id = odoo_15.env['res.currency'].search([('name','=',reconsile_id.debit_move_id.currency_id.name)])
            #print(reconsile_id.debit_move_id.currency_id.name)
            #print(reconsile_id.credit_move_id.currency_id.name)
            credit_currency_id = odoo_15.env['res.currency'].search([('name','=',reconsile_id.credit_move_id.currency_id.name)])

            credit_currency_id = credit_currency_id[0] if reconsile_id.credit_move_id.currency_id.name else 21
            
            debit_currency_id = debit_currency_id[0] if reconsile_id.debit_move_id.currency_id.name else 21

            amount = reconsile['amount']
            
            company_id = odoo_15.env['res.company'].search([('name','=',reconsile_id.company_id.name)])

            debit_amount_currency = reconsile_id.debit_move_id.amount_currency
            credit_amount_currency = reconsile_id.credit_move_id.amount_currency 

            #print(credit_move_id)
            #print(debit_move_id)
            #print(debit_currency_id)
            #print(credit_currency_id)
            #print(company_id)
            print("""\ninsert into account_partial_reconcile (credit_move_id,debit_move_id,
            debit_currency_id,credit_currency_id,amount
            ,company_id,debit_amount_currency,credit_amount_currency) values(""",credit_move_id,""",""",debit_move_id,""",""",
            debit_currency_id,""",""",credit_currency_id,""",""",
            amount,""",""",company_id[0],""",""",debit_amount_currency,""",""",credit_amount_currency,""");""",sep="")
            
