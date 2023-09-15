import odoorpc

# Odoo 9 Environment server and login credentials
odoo_9 = odoorpc.ODOO('192.168.2.44', port=8009)
odoo_9.login('9_hrms_test_2821', 'admin', 'admin')

# Odoo 15 Environment server and login credentials
odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
odoo_15.login('2710_for_tester', 'admin', 'admin')

maintenance_request_fields = ['name', 'mt_sequence_no', 'id', 'request_date', 'employee_id', 'equipment_id',
                              'category_id', 'user_id', 'schedule_date', 'tentative_date', 'company_id',
                              'display_name', 'stage_id']


class CreateMaintenanceRequest:

    def equipment_history_result(self, equip_hist):
        print('\n equipment_history_result', self, 'equip_hist', equip_hist)
        equipment_result = {'name': equip_hist.get('name'),
                            'display_name': equip_hist.get('display_name'),
                            'mt_sequence_no': equip_hist.get('mt_sequence_no'),
                            'tentative_date': equip_hist.get('tentative_date'),
                            'schedule_date': equip_hist.get('schedule_date'),
                            'request_date': equip_hist.get('request_date'),
                            'v9_id': equip_hist.get('id'),
                            }
        return equipment_result

    # Employee
    def fetch_employee(self, values):
        print('\n fetch_employee_id', self, '\n values', values)
        employee = odoo_15.execute('hr.employee', 'search_read',
                                   [['name', '=', values]], ['id'])
        return employee

    # User
    def fetch_user(self, values):
        print('\n fetch_user', self, '\n values', values)
        users = odoo_15.execute('res.users', 'search_read',
                                [['name', '=', values]], ['id'])
        return users

    # Company
    def fetch_company(self, values):
        print('\n fetch_company', self, '\n values', values)
        # stop
        company = odoo_15.execute('res.company', 'search_read',
                                  [['name', '=', values]], ['id'])
        return company

    # Stage
    def fetch_stage(self, values):
        print('\n fetch_stage', self, '\n values', values)
        stage = odoo_15.execute('maintenance.stage', 'search_read',
                                [['name', '=', values]], ['id'])
        return stage

    # Category
    def fetch_category(self, values):
        print('\n fetch_category', self, '\n values', values)
        category = odoo_15.execute('maintenance.equipment.category', 'search_read',
                                   [['name', '=', values]], ['id'])
        return category

    # Equipment
    def fetch_equipment(self, values):
        print('\n fetch_employee_id', self, '\n values', values)
        employee = odoo_15.execute('maintenance.equipment', 'search_read',
                                   [['v9_id', '=', values]], ['id'])
        return employee

    # Equipment History
    def create_maintenance_request(self):
        equipment_request_v9 = odoo_9.execute('hr.equipment.request', 'search_read',
                                              [], maintenance_request_fields)  # ['id', '=', 92]['id', '=', 46]
        print('Length equipment_request_v9 ---- >>>>', len(equipment_request_v9))

        for equip_req in equipment_request_v9:
            maintenance_request = odoo_15.env['maintenance.request']
            # Need to Add v9_emp_id field to Employee module
            existing_rec = maintenance_request.search([('v9_id', '=', equip_req.get('id'))], limit=1)
            if existing_rec:
                print('\n  IF  ', existing_rec)
            else:
                print('\n ELSE equip_hist -->>', equip_req)
                equip_hist_values = self.equipment_history_result(equip_req)
                if equip_req.get('employee'):
                    values = equip_req.get('employee')[1]
                    employee = self.fetch_employee(values)
                    print('\n employee', employee)
                    if employee:
                        equip_hist_values['employee'] = employee[0].get('id')
                    else:
                        equip_hist_values['employee'] = 21
                if equip_req.get('category_id'):
                    values = equip_req.get('category_id')[1]
                    category_id = self.fetch_category(values)
                    print('\n category_id', category_id)
                    if category_id:
                        equip_hist_values['category_id'] = category_id[0].get('id')
                if equip_req.get('user_id'):
                    values = equip_req.get('user_id')[1]
                    user_id = self.fetch_user(values)
                    print('\n user_id', user_id)
                    if user_id:
                        equip_hist_values['user_id'] = user_id[0].get('id')
                if equip_req.get('company_id'):
                    # stop
                    c_values = equip_req.get('company_id')[1]
                    company = self.fetch_company(c_values)
                    print('\n company', company)
                    if company:
                        equip_req['company_id'] = company[0].get('id')
                if equip_req.get('stage_id'):
                    values = equip_req.get('stage_id')[1]
                    stage = self.fetch_stage(values)
                    print('\n stage', stage)
                    if stage:
                        equip_hist_values['stage_id'] = stage[0].get('id')
                if equip_req.get('equipment_id'):
                    values = equip_req.get('equipment_id')[0]
                    equipment_id = self.fetch_equipment(values)
                    print('\n equipment_id', equipment_id)
                    if equipment_id:
                        equip_hist_values['equipment_id'] = equipment_id[0].get('id')
                maintenance_request_of_odoo15 = odoo_15.execute('maintenance.request', 'create', equip_hist_values)
                print('\n Maintenance Request Of Odoo 15 --->>', maintenance_request_of_odoo15)


x = CreateMaintenanceRequest()
x.create_maintenance_request()
print('\n ॐ \n')
