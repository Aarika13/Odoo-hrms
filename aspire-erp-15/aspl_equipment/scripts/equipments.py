import odoorpc

# Odoo 9 Environment server and login credentials
odoo_9 = odoorpc.ODOO('192.168.2.44', port=8009)
odoo_9.login('9_hrms_test_2821', 'admin', 'admin')

# Odoo 15 Environment server and login credentials
odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
odoo_15.login('2710_for_tester', 'admin', 'admin')

magically_fields = ['id', 'create_date', 'write_date', 'write_uid', 'create_uid',
                    '__last_update']

equipment_fields = ['name', 'serial_no', 'purchase_date', 'scrap_date', 'stock_type', 'bill_no', 'partner_ref', 'model',
                    'cost', 'warranty', 'warranty_period', 'warranty_end_date', 'manufacturing', 'category_id',
                    'categ_ids', 'company_id', 'effective_histy', 'id', 'employee_id', 'parent', 'technician_id',
                    'partner_id', 'maintenance_ids']


class CreateEquipment:

    # Tag
    def create_tag(self, values):
        app_cat_list = []
        at_cat_info_v9 = odoo_9.execute('hr.equipment.tag', 'search_read',
                                        [['id', 'in', values]],
                                        ['name'])
        for at_cat in at_cat_info_v9:
            v15_app_cat = odoo_15.env['equipment.tag'].search([('name', '=', at_cat.get('name'))])
            if v15_app_cat:
                app_cat_list.append(v15_app_cat[0])
            else:
                v15_app_cat = odoo_15.execute('equipment.tag', 'create',
                                              {'name': at_cat.get('name')})
                app_cat_list.append(v15_app_cat)
        return app_cat_list

    # Category
    def fetch_category(self, co):
        category = odoo_15.execute('maintenance.equipment.category', 'search_read',
                                   [['name', '=', co]], ['id'])
        return category

    # Manufacturing
    def fetch_manufacturing(self, values):
        manufacturing = odoo_15.execute('equipment.manufacturing', 'search_read',
                                        [['name', '=', values]], ['id'])
        return manufacturing

    # User
    def fetch_user(self, values):
        users = odoo_15.execute('res.users', 'search_read',
                                [['name', '=', values]], ['id'])
        return users

    # Company
    def fetch_company(self, values):
        company = odoo_15.execute('res.company', 'search_read',
                                  [['name', '=', values]], ['id'])
        return company

    # Employee
    def fetch_employee(self, values):
        employee = odoo_15.execute('hr.employee', 'search_read',
                                   [['name', '=', values]], ['id'])
        return employee

    # Vendor
    def fetch_partner(self, values):
        partner = odoo_15.execute('res.partner', 'search_read',
                                  [['name', '=', values]], ['id'])
        return partner

    # Equipment
    def fetch_equipment(self, values):
        equipment = odoo_15.execute('maintenance.equipment', 'search_read',
                                    [['v9_id', '=', values]], ['id'])
        return equipment

    # Equipment Result
    def equipment_result(self, equipment):
        equipment_result = {'name': equipment.get('name'),
                            'serial_no': equipment.get('serial_no'),
                            'purchase_date': equipment.get('purchase_date'),
                            'scrap_date': equipment.get('scrap_date'),
                            'bill_no': equipment.get('bill_no'),
                            'stock_type': equipment.get('stock_type'),
                            'note': equipment.get('note'),
                            'partner_ref': equipment.get('partner_ref'),
                            'model': equipment.get('model'),
                            'cost': equipment.get('cost'),
                            'warranty_date': equipment.get('warranty'),
                            'warranty_period': equipment.get('warranty_period'),
                            'warranty_end_date': equipment.get('warranty_end_date'),
                            'v9_id': equipment.get('id'),
                            }
        return equipment_result

    # Maintenance Requests
    def fetch_maintenance_ids(self, values, equip_rec):
        maintenance_request_fields = ['name', 'mt_sequence_no', 'id', 'request_date', 'employee_id', 'equipment_id',
                                      'category_id', 'user_id', 'schedule_date', 'tentative_date', 'company_id',
                                      'display_name', 'stage_id']
        equipment_request = odoo_9.execute('hr.equipment.request', 'search_read',
                                           [['id', 'in', values]], maintenance_request_fields)
        for er in equipment_request:
            result = {'name': er.get('name'),
                      'display_name': er.get('display_name'),
                      'mt_sequence_no': er.get('mt_sequence_no'),
                      'tentative_date': er.get('tentative_date'),
                      'schedule_date': er.get('schedule_date'),
                      'request_date': er.get('request_date'),
                      'v9_id': er.get('id'),
                      'equipment_id': equip_rec,
                      }
            if er.get('employee_id'):
                employee = odoo_15.execute('hr.employee', 'search_read',
                                           [['name', '=', er.get('employee_id')[1]]], ['id'])
                if employee:
                    result['employee_id'] = employee[0].get('id')
            if er.get('category_id'):
                category_id = odoo_15.execute('maintenance.equipment.category', 'search_read',
                                              [['name', '=', er.get('category_id')[1]]], ['id'])
                if category_id:
                    result['category_id'] = category_id[0].get('id')
            if er.get('user_id'):
                user_id = odoo_15.execute('res.users', 'search_read',
                                          [['name', '=', er.get('user_id')[1]]], ['id'])
                if user_id:
                    result['user_id'] = user_id[0].get('id')
            if er.get('stage_id'):
                stage = odoo_15.execute('maintenance.stage', 'search_read',
                                        [['name', '=', er.get('stage_id')[1]]], ['id'])
                if stage:
                    result['stage_id'] = stage[0].get('id')
            if er.get('company_id'):
                company_id = odoo_15.execute('res.company', 'search_read',
                                             [['name', '=', er.get('company_id')[1]]], ['id'])
                if company_id:
                    result['company_id'] = company_id[0].get('id')
            v15_equipment_request = odoo_15.execute('maintenance.request', 'create', result)
            print('\n v15_equipment_request -->>>', v15_equipment_request)

    # Equipment
    def create_equipment(self):
        equipment_info_v9 = odoo_9.execute('hr.equipment', 'search_read',
                                           [], equipment_fields)  # ['id', '=', 13767]
        print('Length Employee ---- >>>>', len(equipment_info_v9))
        for equipment in equipment_info_v9:
            print('\n Equipment -->>', equipment)
            maintenance_equipment = odoo_15.env['maintenance.equipment']
            existing_rec = maintenance_equipment.search([('v9_id', '=', equipment.get('id'))], limit=1)
            if existing_rec:
                print('\n 154 If existing record ID', existing_rec)
                equipment_id = odoo_15.env['maintenance.equipment'].search(
                    [('id', '=', existing_rec[0])])
                equipment_id = odoo_15.env['maintenance.equipment'].browse(equipment_id)
                vals = {}
                if equipment.get('parent'):
                    values = equipment.get('parent')[0]
                    parent = self.fetch_equipment(values)
                    if parent:
                        vals['parent'] = parent[0].get('id')
                        equipment_id.write(vals)
            else:
                print('\n ELSE equipment -->>', equipment)
                equip_values = self.equipment_result(equipment)
                if equipment.get('manufacturing'):
                    values = equipment.get('manufacturing')[1]
                    manufacturing = self.fetch_manufacturing(values)
                    if manufacturing:
                        equip_values['manufacturing'] = manufacturing[0].get('id')
                if equipment.get('category_id'):
                    c_values = equipment.get('category_id')[1]
                    category = self.fetch_category(c_values)
                    if category:
                        equip_values['category_id'] = category[0].get('id')
                if equipment.get('categ_ids'):
                    values = equipment.get('categ_ids')
                    tag = self.create_tag(values)
                    equip_values['categ_ids'] = tag
                if equipment.get('user_id'):
                    u_values = equipment.get('user_id')[1]
                    user = self.fetch_user(u_values)
                    equip_values['user_id'] = user
                if equipment.get('company_id'):
                    c_values = equipment.get('company_id')[1]
                    company = self.fetch_company(c_values)
                    equip_values['company_id'] = company[0].get('id')
                if equipment.get('employee_id'):
                    values = equipment.get('employee_id')[1]
                    employee = self.fetch_employee(values)
                    if employee:
                        equip_values['employee_id'] = employee[0].get('id')
                if equipment.get('partner_id'):
                    values = equipment.get('partner_id')[1]
                    partner = self.fetch_partner(values)
                    if partner:
                        equip_values['partner_id'] = partner[0].get('id')
                print('\n equip_values', equip_values)
                me_rec = odoo_15.execute('maintenance.equipment', 'create', equip_values)
                print('\n CREATED Record ID : V15', me_rec)
                if equipment.get('maintenance_ids'):
                    values = equipment.get('maintenance_ids')
                    self.fetch_maintenance_ids(values, me_rec)


x = CreateEquipment()
x.create_equipment()
print('\n ॐ \n')
