from credentials import odoo_9,odoo_15


product_list = ['name','type','sale_ok','invoice_policy','track_service','gst_service_code','list_price','property_account_income_id','standard_price','uom_id']
product_detail = odoo_9.execute('product.template','search_read',[],product_list)

for product in product_detail:
    print(product)
    product_id = odoo_15.env['product.template'].search([('name','=',product['name'])])
    
    if not product_id:
        if product['property_account_income_id']:
            property_account_income_id = odoo_15.env['account.account'].search([('code','=',product['property_account_income_id'][1].split(' ',1)[0]),('name','=',product['property_account_income_id'][1].split(' ',1)[1])])
        else:
            property_account_income_id = []
        
        if product['gst_service_code']:
            gst_service_code = odoo_9.env['product.gst.code'].browse(product['gst_service_code'][0])
        else:
            gst_service_code = []

        if product['uom_id']:  
            uom_id= odoo_15.env['uom.uom'].search([('name','ilike',product['uom_id'][1].split('(')[0])])
        else:
            uom_id = []
           
        
        product_data = {
                'name':product.get('name'),
                'detailed_type':product.get('type'),
                'sale_ok':product.get('sale_ok'),
                'list_price':product.get('list_price'),
                'standard_price':product.get('standard_price'),
                'l10n_in_hsn_code':gst_service_code.name if gst_service_code else '',
                'l10n_in_hsn_description':gst_service_code.description if gst_service_code else '',
                'property_account_income_id':property_account_income_id[0] if property_account_income_id else '',
                'uom_id':uom_id[0] if uom_id else ''
                }


        if product['type'] == 'service':
            if product['track_service'] == 'manual':
                service_policy = 'delivered_manual'
            elif product['track_service'] == 'timesheet':
                service_policy = 'delivered_timesheet'
            elif product['track_service'] == 'task':
                service_policy = 'ordered_timesheet'

           # product_data['service_policy'] = service_policy
            
        if product['type'] == 'consu':
            invoice_policy = product['invoice_policy']
            product_data['invoice_policy'] = invoice_policy
        print(product_data)
        v_15_attachment_id = odoo_15.execute('product.template', 'create', product_data)
        
print("Done")