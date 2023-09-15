import odoorpc

# Odoo 9 Environment server and login credentials
odoo_9 = odoorpc.ODOO('192.168.2.44', port=8009)
odoo_9.login('9_hrms_test_2821', 'admin', 'admin')

# Odoo 15 Environment server and login credentials
odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
odoo_15.login('2710_for_tester', 'admin', 'admin')

equipment_fields = ['warranty', 'id', 'equipment_sequence_no', 'warranty_end_date']

users_fields = ['id', 'login', 'email']


class UpdateEquipmentUsers:

    # Equipment
    def update_equipment(self):
        equipment_info_v9 = odoo_9.execute('hr.equipment', 'search_read',
                                           [], equipment_fields)
        print('Length Equipment ---- >>>>', len(equipment_info_v9))
        for equipment in equipment_info_v9:
            print('\n Equipment -->>', equipment)
            maintenance_equipment = odoo_15.env['maintenance.equipment']
            existing_rec = maintenance_equipment.search([('v9_id', '=', equipment.get('id'))], limit=1)
            if existing_rec:
                print('\n existing_rec', existing_rec)
                equipment_id = odoo_15.env['maintenance.equipment'].search(
                    [('id', '=', existing_rec[0])])
                equipment_id = odoo_15.env['maintenance.equipment'].browse(equipment_id)
                vals = {}
                if equipment.get('warranty'):
                    vals['warranty'] = equipment.get('warranty')
                if equipment.get('warranty_end_date'):
                    vals['warranty_date'] = equipment.get('warranty_end_date')
                if equipment.get('equipment_sequence_no'):
                    vals['equipment_sequence_no'] = equipment.get('equipment_sequence_no')
                equipment_id.write(vals)

    # Update Users Email
    def update_users_email(self):
        users = odoo_15.execute('res.users', 'search_read',
                                [], users_fields)
        print('Length users ---- >>>>', len(users))
        for user in users:
            print('\n Users -->>', user)
            res_users = odoo_15.env['res.users']
            existing_rec = res_users.search([('id', '=', user.get('id'))], limit=1)
            if existing_rec:
                print('\n existing_rec', existing_rec)
                users_id = odoo_15.env['res.users'].search(
                    [('id', '=', existing_rec[0])])
                users_id = odoo_15.env['res.users'].browse(users_id)
                vals = {}
                if user.get('login'):
                    vals['email'] = user.get('login')
                users_id.write(vals)


x = UpdateEquipmentUsers()
x.update_equipment()
x.update_users_email()
print('\n ॐ \n')
