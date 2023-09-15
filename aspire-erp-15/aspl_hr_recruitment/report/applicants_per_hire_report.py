# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ApplicantsPerHire(models.Model):
    _name = "applicants.per.hire"
    _description = 'Applicants Per Hire Report'
    _auto = False

    job_opening_id = fields.Many2one(comodel_name='job.opening', string='Job Opening')
    appl_per_hire = fields.Float('Joined Count')

    def init(self):
        """ Job Opening """
        tools.drop_view_if_exists(self._cr, 'applicants_per_hire')
        self._cr.execute("""
                            CREATE OR REPLACE VIEW applicants_per_hire AS (
                                SELECT 
                                row_number() OVER () as id,
                                otr.id as job_opening_id,
                                round(Applicants::decimal/Hired,2) AS appl_per_hire
                                FROM (select o.id,o.Applicants, count(o.id) AS Hired
                                        FROM (select o.id,o.name,count(a.id) AS applicants
                                            FROM job_opening o
                                            join hr_applicant a on a.job_opening_id = o.id 
                                            group by o.id,o.name 
                                            )o
                                            join hr_applicant a on a.job_opening_id = o.id 
                                            join hr_recruitment_stage stg on stg.id = a.stage_id 
                                            where stg.name = 'Offered' 
                                            group by o.id, o.applicants
                                    ) AS otr

                            )""")
