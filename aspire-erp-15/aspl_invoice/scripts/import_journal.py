from credentials import odoo_9,odoo_15

account_journal_field = ['name','code','type','default_credit_account_id','currency_id','company_id','profit_account_id','loss_account_id','bank_account_id',
                         'create_uid','create_date','write_uid','write_date','show_on_dashboard']

account_journal_detail = odoo_9.execute('account.journal','search_read',[],account_journal_field)

for journal in account_journal_detail:
    journal_id = odoo_15.env['account.journal'].search([('name','=',journal['name'])])
   
    if not journal_id:
        #default_account_id = odoo_15.env['account.account'].search([('code','=',journal['default_credit_account_id'][1].split(' ')[0]),('name','=',journal['default_credit_account_id'][1].split(' ')[1])])

        if journal['currency_id']:
            currency_id = odoo_15.env['res.currency'].search([('name','=',journal['currency_id'][1])])
        else:
            currency_id = []

        if journal['company_id']:
            company_id = odoo_15.env['res.company'].search([('name','=',journal['company_id'][1])])
        else:
            company_id = []

        if journal['profit_account_id']:
            profit_account_id = odoo_15.env['account.account'].search([('code','=',journal['profit_account_id'][1].split(' ')[0]),('name','=',journal['profit_account_id'][1].split(' ')[1])])
        else:
            profit_account_id = []

        if journal['loss_account_id']:
            loss_account_id = odoo_15.env['account.account'].search([('code','=',journal['loss_account_id'][1].split(' ')[0]),('name','=',journal['loss_account_id'][1].split(' ')[1])])
        else:
            loss_account_id = []

        if journal['bank_account_id']:
            bank_account_id = odoo_15.env['res.partner.bank'].search([('acc_number','=',journal['bank_account_id'][1])])
        else:
            bank_account_id = []

        if journal['create_uid']:
            create_uid = odoo_15.env['res.users'].search([('name','=',journal['create_uid'][1])])
        else:
            create_uid = []

        if journal['write_uid']:
            write_uid = odoo_15.env['res.users'].search([('name','=',journal['write_uid'][1])])
        else:
            write_uid = []  

        
        account_journal_data = {
            'name':journal.get('name'),
            'code':journal.get('code'),
            'type':journal.get('type'),
            #'show_on_dashboard':journal.get('show_on_dashboard'),
            #'default_account_id':default_account_id[0] if default_account_id else '',
            'currency_id':currency_id[0] if currency_id else '',
            'company_id':company_id[0] if company_id else '',
            #'profit_account_id':profit_account_id[0] if profit_account_id else '',
            #'loss_account_id':loss_account_id[0] if loss_account_id else '',
            #'bank_account_id':bank_account_id[0] if bank_account_id else '',
            'create_uid':create_uid[0] if create_uid else '',
            'write_uid':write_uid[0] if write_uid else '',
            'create_date':journal.get('create_date'),
            'write_date':journal.get('write_date'), 
            }
        print(account_journal_data)
        v_15_attachment_id = odoo_15.execute('account.journal', 'create', account_journal_data)