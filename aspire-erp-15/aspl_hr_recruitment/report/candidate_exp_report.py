# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class CandidateExp(models.Model):
    _name = "candidate.exp"
    _description = 'Candidate Experience Report'
    _auto = False

    opening_id = fields.Many2one(comodel_name='job.opening', string='Job Opening')
    recruiter_id = fields.Many2one(comodel_name='res.users', string='Recruiter')
    rat_1 = fields.Char('Rating 1')
    rat_2 = fields.Char('Rating 2')
    rat_3 = fields.Char('Rating 3')
    rat_4 = fields.Char('Rating 4')
    rat_5 = fields.Char('Rating 5')

    def init(self):
        """ Candidate Experience Report"""
        tools.drop_view_if_exists(self._cr, 'candidate_exp')
        self._cr.execute("""
                        CREATE OR REPLACE VIEW candidate_exp AS (
                            SELECT
                            row_number() OVER () as id,
                            otr.id as opening_id,
                            otr.user_id as recruiter_id,
case when rat_1 = 1 then 'Very Poor' when rat_1 = 2 then 'Poor' when rat_1 = 3 then 'Average' when rat_1 = 4 then 'Good' else 'Excellent' end rat_1,
case when rat_2 = 1 then 'Very Poor' when rat_2 = 2 then 'Poor' when rat_2 = 3 then 'Average' when rat_2 = 4 then 'Good' else 'Excellent' end rat_2,
case when rat_3 = 1 then 'Very Poor' when rat_3 = 2 then 'Poor' when rat_3 = 3 then 'Average' when rat_3 = 4 then 'Good' else 'Excellent' end rat_3,
case when rat_4 = 1 then 'Very Poor' when rat_4 = 2 then 'Poor' when rat_4 = 3 then 'Average' when rat_4 = 4 then 'Good' else 'Excellent' end rat_4,
case when rat_5 = 1 then 'Very Poor' when rat_5 = 2 then 'Poor' when rat_5 = 3 then 'Average' when rat_5 = 4 then 'Good' else 'Excellent' end rat_5
                           
                        FROM (select
                                o.user_id,
                                o.id,
                                ceiling(AVG(CAST(a.rating1 as float))) as rat_1,
                                ceiling(AVG(CAST(a.rating2 as float))) as rat_2,
                                ceiling(AVG(CAST(a.rating3 as float))) as rat_3,
                                ceiling(AVG(CAST(a.rating4 as float))) as rat_4,
                                ceiling(AVG(CAST(a.rating5 as float))) as rat_5
                                    from job_opening o
                                        join hr_applicant a on a.job_opening_id = o.id
                                        join hr_recruitment_stage stg on stg.id = a.stage_id
                                        where stg.name = 'Offered' and a.feedback_status = True
                                        group by o.user_id, o.id
                                ) AS otr
                        )""")
