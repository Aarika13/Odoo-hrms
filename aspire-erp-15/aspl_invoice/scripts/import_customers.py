from credentials import odoo_9,odoo_15

#Import Payment Swift Detail from Odoo9 to Odoo15


payment_swift_field = ['name','our_correspondence_bank_account_no','our_correspondence_bank_swift_code','routing_no','iban_no','currency']

payment_swift_detail = odoo_9.execute('payment.swift.detials','search_read',[],payment_swift_field)

for payment in payment_swift_detail:
    payment_id = odoo_15.env['payment.swift.details'].search([('name','=',payment['name'])])
    currency_id = odoo_15.env['res.currency'].search([('name','=',payment['currency'][1])])

    if not payment_id:
        res_payment_swift_data = {
            'name':payment.get('name'),
            'our_correspondence_bank_account_no':payment.get('our_correspondence_bank_account_no'),
            'our_correspondence_bank_swift_code':payment.get('our_correspondence_bank_swift_code'),
            'routing_no':payment.get('routing_no'),
            'iban_no':payment.get('iban_no'),
            'currency':currency_id[0],
            }

        v_15_attachment_id = odoo_15.execute('payment.swift.details', 'create', res_payment_swift_data)
       

#Payment Term Detail from odoo

payment_Term_field = ['name','company_id']

payment_Term_detail = odoo_9.execute('account.payment.term','search_read',[],payment_Term_field)

for payment in payment_Term_detail:
    
    company_id = odoo_15.env['res.company'].search([('name','=',payment['company_id'][1])])
    payment_id = odoo_15.env['account.payment.term'].search([('name','=',payment['name'])])
    if not payment_id:
        res_payment_swift_data = {
                'name':payment.get('name'),
                'company_id':company_id[0],
                }

        v_15_attachment_id = odoo_15.execute('account.payment.term', 'create', res_payment_swift_data)
    


# Account Detail import from odoo9 to odoo15

customer_account_field = ['name','code','user_type_id','company_id']

customer_account_detail = odoo_9.execute('account.account','search_read',[],customer_account_field)

for account in customer_account_detail:
    account_id =odoo_15.env['account.account'].search([('name','=',account['name']),('code','=',account['code'])])
    user_type_id = odoo_15.env['account.account.type'].search([('name','=',account['user_type_id'][1])])
    company_id = odoo_15.env['res.company'].search([('name','=',account['company_id'][1])])
    if not account_id:
        customer_account_data = {
                'name':account.get('name'),
                'code':account.get('code'),
                'user_type_id':user_type_id[0],
                'company_id':company_id[0],
                }

        v_15_attachment_id = odoo_15.execute('account.account', 'create', customer_account_data)

#Import Customers from Odoo9 to Odoo15

customer_field = ['customer','name','street','street2','city','state_id','zip','country_id'
                  ,'phone','mobile','email','currency','website','payment_detial','gstin','property_payment_term_id',
                  'property_account_payable_id','property_account_receivable_id','company_type','child_ids']



customer = odoo_9.execute('res.partner','search_read',[],customer_field)

for customer in customer:
    print(customer)
    if customer.get('customer'):
        customer_id = odoo_15.env['res.partner'].search([('name','=',customer['name'])])
    
        if not customer_id:
            currency_id = []
            state_id = []
            country_id = []
            payment_detial = []
            property_payment_term_id = []
            property_account_receivable_id = []
            property_account_payable_id = []
            
            if customer['currency']:
                currency_id = odoo_15.env['res.currency'].search([('name','=',customer['currency'][1])])
               
            if customer['state_id']:
                state_id = odoo_15.env['res.country.state'].search([('name','=',customer['state_id'][1])])
                
            if customer['country_id']:
                country_id = odoo_15.env['res.country'].search([('name','=',customer['country_id'][1])])


            if customer['payment_detial']:
                payment_detial = odoo_15.env['payment.swift.details'].search([('name','=',customer['payment_detial'][1])])

            if customer['property_payment_term_id']:
                property_payment_term_id = odoo_15.env['account.payment.term'].search([('name','=',customer['property_payment_term_id'][1])])

            if customer['property_account_receivable_id']:
                property_account_receivable_id = odoo_15.env['account.account'].search([('name','=',customer['property_account_receivable_id'][1].split(' ')[1]),('code','=',customer['property_account_receivable_id'][1].split(' ')[0])])

            if customer['property_account_payable_id']:
                property_account_payable_id = odoo_15.env['account.account'].search([('name','=',customer['property_account_payable_id'][1].split(' ')[1]),('code','=',customer['property_account_payable_id'][1].split(' ')[0])])

            
            res_customer_data = {
                'name':customer.get('name'),
                'street':customer.get('street'),
                'street2':customer.get('street2'),
                'city':customer.get('city'),
                'state_id':state_id[0] if state_id else '',
                'zip':customer.get('zip'),
                'company_type':customer.get('company_type'),
                'country_id':country_id[0],
                'phone':customer.get('phone'),
                'mobile':customer.get('mobile'),
                'email':customer.get('email'),
                'website':customer.get('website'),
                'gstin':customer.get('gstin'),
                'currency':currency_id[0] if currency_id else '',
                'payment_detial':payment_detial[0] if payment_detial else '',
                'property_payment_term_id':property_payment_term_id[0] if property_payment_term_id else '',
                'property_account_receivable_id':property_account_receivable_id[0] if property_account_receivable_id else '',
                'property_account_payable_id':property_account_payable_id[0] if property_account_payable_id else '',
                }

            v_15_attachment_id = odoo_15.execute('res.partner', 'create', res_customer_data)   
    
#child_ids from odoo9 to odoo15

for customer in customer: 
    print(customer)
    if customer.get('customer') and customer.get('child_ids'):

        customer_id = odoo_15.env['res.partner'].search([('name','=',customer['name'])])
        child_data = []
        for child_id in customer.get('child_ids'):
            odoo9_child_id = odoo_9.env['res.partner'].browse(child_id)
            child_ids = odoo_15.env['res.partner'].search([('name','=',odoo9_child_id.name)])
            child_data.append(child_ids[0])

        res_customer_data = {
            'child_ids':child_data,
            'v9_an_id':customer['id']
            }
        v_15_attachment_id = odoo_15.execute_kw('res.partner', 'write',[customer_id,res_customer_data])
    

#V9_id from odoo9 to odoo15

customer_field = ['customer','name','street','street2','city','state_id','zip','country_id'
                  ,'phone','mobile','email','currency','website','payment_detial','gstin','property_payment_term_id',
                  'property_account_payable_id','property_account_receivable_id','company_type','child_ids']



customer = odoo_9.execute('res.partner','search_read',[],customer_field)

for customer in customer:
    if customer.get('customer'):
        customer_id = odoo_15.env['res.partner'].search([('name','=',customer['name'])])

        res_customer_data = {
            'v9_id':customer['id']
            }

        v_15_attachment_id = odoo_15.execute_kw('res.partner', 'write',[customer_id,res_customer_data])