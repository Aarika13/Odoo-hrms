import odoorpc

# Odoo 15 Environment server and login credentials
# odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
# odoo_15.login('2710_for_tester', 'admin', 'admin')
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('test_04Apr', 'admin', 'admin')

attach_fields = ['id']
candidate_Odoo15 = odoo_15.execute('candidate', 'search_read', [['is_applicant', '=', True]], attach_fields)
print('Length Res Partner -->>', len(candidate_Odoo15))
for asp_candidate in candidate_Odoo15:
    print("\nCandidate->", asp_candidate)
    applicant = odoo_15.env['hr.applicant'].search([('candidate_id', '=', int(asp_candidate.get('id')))])
    if applicant:
        applicant_obj = odoo_15.env['hr.applicant'].browse(applicant[0])
        if applicant_obj:
            applicant_obj.update({
                'is_candidate': True,
             })
            print("------------------------Applicant_Updated_with_is_candidate_______________________________")

print('\n========== OM ==========\n')
