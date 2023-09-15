# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class OfferAccPerHire(models.Model):
    _name = "offer.acc.per.hire"
    _description = 'Offer acceptance Per Hire Report'
    _auto = False

    job_opening_id = fields.Many2one(comodel_name='job.opening', string='Job Opening')
    ofr_acc = fields.Float('Offer Accepted')
    ofr_hire = fields.Float('Offer Hired')
    ofr_ave = fields.Float('Offer Accept/Hire Average')

    def init(self):
        """ Job Opening """
        tools.drop_view_if_exists(self._cr, 'offer_acc_per_hire')
        self._cr.execute("""CREATE OR REPLACE VIEW offer_acc_per_hire AS (
                SELECT 
                row_number() OVER () as id,
                otr.id as job_opening_id,
                round(ofr_acc::decimal) AS ofr_acc,
                round(Hired::decimal) AS ofr_hire,
                case when Hired= 0 then 0 else round(ofr_acc::decimal/Hired,2) end AS ofr_ave
                FROM (select o.id,
                        count(a.id) ofr_acc,
                        sum(case when a.offer = 'joined' then 1 else 0 end) AS Hired
                            FROM job_opening o
                            join hr_applicant a on a.job_opening_id = o.id 
                            join hr_recruitment_stage stg on stg.id = a.stage_id 
                            where stg.name = 'Offered' and a.offer in ('accepted','joined')
                            group by o.id
                    ) AS otr
                            )""")
