import odoorpc

# Odoo 15 Environment server and login credentials
# odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
# odoo_15.login('2710_for_tester', 'admin', 'admin')
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('test_04Apr', 'admin', 'admin')

attach_fields = ['res_id', 'res_model']
attachment_Odoo15 = odoo_15.execute('ir.attachment', 'search_read', [['res_id', '=', 2250], ['res_model', '=', 'candidate']], attach_fields)
print('Length Application -->>', len(attachment_Odoo15))
attachment_not_found = []
for candi in attachment_Odoo15:
    print("\nData->", candi)
    partner_check = odoo_15.env['res.partner'].search(
        [('aspire_candidate_id', '=', int(candi.get('res_id')))], limit=1)
    print("Prev Partner Id", partner_check)
    if partner_check:
        print("----------------------------------INSIDE______________________________________")
        attachment_obj = odoo_15.env['ir.attachment'].browse(int(candi.get('id')))
        print("Attachment", attachment_obj)
        if attachment_obj:
            attachment_obj.update({
                'res_id': partner_check[0],
                'res_model': 'res.partner',
            })
            print("------------------------Ir_Attachment_Record_Updated_______________________________")

print("Attachment Not Found\n", attachment_not_found)
print('\n========== OM ==========\n')
