import odoorpc

# Odoo 15 Environment server and login credentials
# odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
# odoo_15.login('2710_for_tester', 'admin', 'admin')
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('test_04Apr', 'admin', 'admin')

attach_fields = ['id', 'email']
res_partner_Odoo15 = odoo_15.execute('res.partner', 'search_read', [['is_applicant', '=', True]], attach_fields)
print('Length Res Partner -->>', len(res_partner_Odoo15))
for res_partner in res_partner_Odoo15:
    print("\nRes Partner->", res_partner)
    applicant = odoo_15.env['hr.applicant'].search([('partner_id', '=', int(res_partner.get('id')))])
    if applicant:
        applicant_obj = odoo_15.env['hr.applicant'].browse(applicant[0])
        if applicant_obj:
            applicant_obj.update({
                'is_partner': True,
            })
            print("------------------------Applicant_Updated_with_is_partner_______________________________")

print('\n========== OM ==========\n')
