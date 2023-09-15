import odoorpc

# Odoo 15 Environment server and login credentials
# odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
# odoo_15.login('dup_deployment', 'admin', 'admin')
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('test_04Apr', 'admin', 'admin')

partner_fields = ['partner_id']
applicant_Odoo15 = odoo_15.execute('hr.applicant', 'search_read', [], partner_fields)  # ['id', '=', 1192]
# ['id', '=', 1192]
print('Length Application -->>', len(applicant_Odoo15))
applicant_list = []
applicant_without_partner = []
for res_partner in applicant_Odoo15:
    print("\nData->", res_partner)
    if res_partner.get('partner_id'):
        candidate_check = odoo_15.env['candidate'].search(
            [('res_partner_id', '=', int(res_partner.get('partner_id')[0]))], limit=1)
        print("Candidate Record Id", candidate_check)
        if candidate_check:
            print("----------------------------------INSIDE______________________________________")
            applicant_obj = odoo_15.env['hr.applicant'].browse(int(res_partner.get('id')))
            print("Applicant Obj", applicant_obj)
            applicant_obj.update({
                'candidate_id': candidate_check[0],
            })
            print("-------------------Applicant Record Updated with Candidate Id______________________________")
        else:
            applicant_list.append(res_partner.get('partner_id'))
            print("------------No Candidate Found For_____", res_partner.get('partner_id'), "__________________")
    else:
        applicant_without_partner.append(res_partner.get('id'))
        print("------------No Partner Found For_____", res_partner.get('id'), "__________________")

print("Applicant list whose candidate not found\n", applicant_list, "\n")
print("Applicant list whose partner not set\n", applicant_without_partner, "\n")
print('\n========== OM ==========\n')
