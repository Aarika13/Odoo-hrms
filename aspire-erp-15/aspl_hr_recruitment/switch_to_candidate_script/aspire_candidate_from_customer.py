import odoorpc

current_odoo = odoorpc.ODOO('localhost',port='8666')
current_odoo.login('testInvoice1', 'admin', 'admin')

mail_list = ['gmail','outlook','yahoo','rediff']
administrator_user = current_odoo.env['res.users'].search(['&',
                                                           ('login','in',['__system__','admin@aspiresoftserv.com']),
                                                           '|',
                                                           ('active','=',False),('active','=',True)
                                                           ])

domain_mail =['&']+[('street','=',False)]+['&']+[('v9_an_id','=',False)]+['&']+[('aspire_candidate_id','=',False)]+['&']+[('create_uid','in',administrator_user)]+ ['&'] + [('user_id','=',None)] + ['|', '|', '|'] + [('email', 'ilike', domain) for domain in mail_list]

contact_with_email = current_odoo.env['res.partner'].search(domain_mail)
contact_with_email_records = current_odoo.env['res.partner'].browse(contact_with_email)


for contact in contact_with_email_records:

    available_candidate = current_odoo.env['candidate'].search([('email','=',contact.email)])
    if len(available_candidate) == 1:
        available_candidate_id = current_odoo.env['candidate'].browse(available_candidate[0])
        dict_data = {
            'email':contact.email,
            }
        if contact.mobile and contact.mobile != available_candidate_id.mobile:
            dict_data['mobile'] = contact.mobile
        if contact.name and contact.name != available_candidate_id.name:
            dict_data['name'] = contact.name
        available_candidate_id.write(dict_data)

    else:
        candidate_dict = {
            'mobile':contact.mobile,
            'name':contact.name,
            'email':contact.email,
        }
        candidate = current_odoo.execute('candidate', 'create', candidate_dict)
        contact_mail_message = current_odoo.env['mail.message'].search([('res_id','=',contact.id),('model','=','res.partner')])
        
        if len(contact_mail_message) >= 1:
            contact_mail_message_records = current_odoo.env['mail.message'].browse(contact_mail_message)
            for mail_message in contact_mail_message_records:
                new_mail_id = current_odoo.execute('mail.message', 'copy', mail_message.id, {'model': 'candidate','res_id':candidate})
        
        contact_attachment = current_odoo.env['ir.attachment'].search([('res_id','=',contact.id),('res_model','=','res.partner')])
        if len(contact_attachment) >= 1:
            contact_attachment_records = current_odoo.env['ir.attachment'].browse(contact_attachment)
            for attachment in contact_attachment_records:
                new_attachment_id = current_odoo.execute('ir.attachment','copy', attachment.id, {'res_model':'candidate','res_id':candidate})

print(":::::::::::::::success:::::::::::::::")
