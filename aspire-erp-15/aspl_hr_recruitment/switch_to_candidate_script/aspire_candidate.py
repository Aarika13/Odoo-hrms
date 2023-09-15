import odoorpc

# Odoo 15 Environment server and login credentials
# odoo_15 = odoorpc.ODOO('192.168.2.110', port=8069)
# odoo_15.login('2710_for_tester', 'admin', 'admin')
odoo_15 = odoorpc.ODOO('localhost', port=8017)
odoo_15.login('test_04Apr', 'admin', 'admin')

candidate_fields = ['id', 'name', 'mobile', 'email', 'type_id', 'job_id', 'current_company_id',
                    'current_location_city', 'create_date', 'date_received', 'stage', 'categ_ids', 'salary_current',
                    'salary_expected', 'partner_id', 'is_applicant', 'is_candidate',
                    'is_employee', 'in_application', 'active_employee', 'total_exp_years',
                    'total_exp', 'current_experience', 'linked_in_profile', 'year_of_passing',
                    'job_opening_id', 'job_opening_ids', 'v9_an_id', 'source_id',
                    'user_id', 'sourced_by', 'candidate_skill_ids', 'all_application_count',
                    'private_note', 'description', 'app_status', 'active']
res_partner_Odoo15 = odoo_15.execute('res.partner', 'search_read', [['is_candidate', '=', True]],
                                     candidate_fields)  # ['employee_id', '=', 172],
print('Length Application -->>', len(res_partner_Odoo15))
duplicate_record = []

for res_candidate in res_partner_Odoo15:
    print(res_candidate)
    candidate_check = odoo_15.env['candidate'].search(
        [('res_partner_id', '=', int(res_candidate.get('id')))], limit=1)
    print("Prev Candidate Id", candidate_check)
    skill_vals = []
    if candidate_check:
        print('----------------------------------------EXIST---------------------------------------------------')
    else:
        dup_candidate = odoo_15.env['candidate'].search(
            [('email', '=', res_candidate.get('email').strip() if res_candidate.get('email') else res_candidate.get('email'))], limit=1)
        if dup_candidate:
            duplicate_record.append((('Res Partner', res_candidate.get('id')), ('Candidate', dup_candidate)))
            print("----------Candidate Already Exist with Same Mail------------")
        else:
            candidate_vals = {
                'res_partner_id': res_candidate.get('id'),
                'name': res_candidate.get('name'),
                'mobile': res_candidate.get('mobile'),
                'email': res_candidate.get('email').strip(),
                'date_received': res_candidate.get('date_received'),
                'stage': res_candidate.get('stage'),
                'salary_current': res_candidate.get('salary_current'),
                'salary_expected': res_candidate.get('salary_expected'),
                'is_applicant': res_candidate.get('is_applicant'),
                'is_candidate': res_candidate.get('is_candidate'),
                'is_employee': res_candidate.get('is_employee'),
                'in_application': res_candidate.get('in_application'),
                'active_employee': res_candidate.get('active_employee'),
                'total_exp_years': res_candidate.get('total_exp_years'),
                'total_exp': res_candidate.get('total_exp'),
                'current_experience': res_candidate.get('current_experience'),
                'linked_in_profile': res_candidate.get('linked_in_profile'),
                'year_of_passing': res_candidate.get('year_of_passing'),
                'v9_an_id': res_candidate.get('v9_an_id'),
                # 'all_application_count': res_candidate.get('all_application_count'),
                'private_note': res_candidate.get('private_note'),
                'description': res_candidate.get('description'),
                'app_status': res_candidate.get('app_status'),
                'active': res_candidate.get('active'),
                'partner_create_date': res_candidate.get('create_date').split()[0],

            }
            if res_candidate.get('type_id'):
                candidate_vals['type_id'] = res_candidate.get('type_id')[0]

            if res_candidate.get('job_id'):
                candidate_vals['job_id'] = res_candidate.get('job_id')[0]

            if res_candidate.get('current_company_id'):
                candidate_vals['current_company_id'] = res_candidate.get('current_company_id')[0]

            if res_candidate.get('current_location_city'):
                candidate_vals['current_location_city'] = res_candidate.get('current_location_city')[0]

            if res_candidate.get('partner_id'):
                candidate_vals['partner_id'] = res_candidate.get('partner_id')[0]

            if res_candidate.get('source_id'):
                candidate_vals['source_id'] = res_candidate.get('source_id')[0]

            if res_candidate.get('sourced_by'):
                candidate_vals['sourced_by'] = res_candidate.get('sourced_by')[0]

            if res_candidate.get('job_opening_id'):
                candidate_vals['job_opening_id'] = res_candidate.get('job_opening_id')[0]
            else:
                if res_candidate.get('is_candidate'):
                    if res_candidate.get('job_opening_ids'):
                        candidate_vals['job_opening_id'] = res_candidate.get('job_opening_ids')[-1]

            if res_candidate.get('categ_ids'):
                candidate_vals['categ_ids'] = res_candidate.get('categ_ids')

            if res_candidate.get('job_opening_ids'):
                candidate_vals['job_opening_ids'] = res_candidate.get('job_opening_ids')

            if res_candidate.get('candidate_skill_ids'):
                candidate_vals['candidate_skill_ids'] = res_candidate.get('candidate_skill_ids')

            v_15_candidate_id = odoo_15.execute('candidate', 'create', candidate_vals)

            print('--------------------------------Candidate Created------------------------------------------')

print("\nDuplicate Email Records", duplicate_record)
print('\n========== OM ==========\n')
