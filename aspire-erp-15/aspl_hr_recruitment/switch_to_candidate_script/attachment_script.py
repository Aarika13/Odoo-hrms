import odoorpc

# Odoo 15 Environment server and login credentials
# odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
# odoo_15.login('2710_for_tester', 'admin', 'admin')
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('test_04Apr', 'admin', 'admin')

attach_fields = ['res_id', 'res_model']
attachment_Odoo15 = odoo_15.execute('ir.attachment', 'search_read', [['res_id', '=', 374], ['res_model', '=', 'res.partner']], attach_fields)
print('Length Application -->>', len(attachment_Odoo15))
candidate_not_found = []
attachment_not_found = []
for res_partner in attachment_Odoo15:
    print("\nData->", res_partner)
    candidate_check = odoo_15.env['candidate'].search(
        [('res_partner_id', '=', int(res_partner.get('res_id')))], limit=1)
    print("Prev Candidate Id", candidate_check)
    skill_vals = []
    if candidate_check:
        print("----------------------------------INSIDE______________________________________")
        attachment_obj = odoo_15.env['ir.attachment'].browse(int(res_partner.get('id')))
        res_partner_obj = odoo_15.env['res.partner'].browse(int(res_partner.get('res_id')))
        print("Attachment", attachment_obj)
        if attachment_obj:
            attachment_obj.update({
                'res_id': candidate_check[0],
                'res_model': 'candidate',
            })
            print("------------------------Ir_Attachment_Record_Updated_______________________________")
        else:
            attachment_not_found.append(res_partner.get('res_id'))
            print("--------------------------Attachment_Not_Found____________________________________")
        if res_partner_obj:
            res_partner_obj.update({
                'aspire_candidate_id': candidate_check[0]
            })
            print("--------------------------Partner_Updated_with_Candi_Id_____________________________")
    else:
        candidate_not_found.append(res_partner.get('res_id'))
        print("------------Candidate_Not_Found_____________________________________")

print("Candidate Not Found\n", candidate_not_found, "\n")
print("Attachment Not Found\n", attachment_not_found)
print('\n========== OM ==========\n')
