from credentials import odoo_9,odoo_15

account_move_line = ['id']
account_move_line_detail = odoo_9.execute('account.move.line','search_read',[],account_move_line)

print("account_move_line_detail == ",account_move_line_detail)
for move_line in account_move_line_detail:
   
    odoo9_account_move_line = odoo_9.env['account.move.line'].browse(move_line['id'])

    if odoo9_account_move_line.tax_ids:

        for tax_id in odoo9_account_move_line.tax_ids:
            odoo_15_tax_id = odoo_15.env['account.tax'].search([('name','=',tax_id.name)])
            odoo_15_move_line_id = odoo_15.env['account.move.line'].search([('v9_id','=',odoo9_account_move_line.id)])

            print("""insert into account_move_line_account_tax_rel (account_move_line_id,account_tax_id) values (""",odoo_15_move_line_id,""",""",odoo_15_tax_id,""")""")
            
