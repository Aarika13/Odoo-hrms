# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class VacanciesVsFilled(models.Model):
    _name = "vacancies.vs.filled"
    _description = 'Vacancies vs Filled Report'
    _auto = False

    job_opening_id = fields.Many2one(comodel_name='job.opening', string='Job Opening')
    vacancies = fields.Float('Vacancies')
    filled = fields.Float('Filled')

    def init(self):
        """ Job Opening """
        tools.drop_view_if_exists(self._cr, 'vacancies_vs_filled')
        self._cr.execute("""
                            CREATE OR REPLACE VIEW vacancies_vs_filled AS (
                                SELECT 
                                row_number() OVER () as id,
                                otr.id as job_opening_id,
                                otr.no_of_recruitment as vacancies,
                                hire as filled
                                FROM (select o.no_of_recruitment,o.id, count(a.id) AS Hire                                        
                                            from job_opening o 
                                            join hr_applicant a on a.job_opening_id = o.id 
                                            join hr_recruitment_stage stg on stg.id = a.stage_id 
                                            where stg.name = 'Offered' 
                                            group by o.no_of_recruitment, o.id
                                    ) AS otr

                            )""")
