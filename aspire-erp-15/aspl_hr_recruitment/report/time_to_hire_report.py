# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class TimeToHire(models.Model):
    _name = "time.to.hire"
    _description = 'Time To Hire Report'
    _auto = False

    job_opening_id = fields.Many2one(comodel_name='job.opening', string='Job Opening')
    applicant_id = fields.Many2one(comodel_name='hr.applicant', string='Applicant')
    screen_time = fields.Float('Screened Time')
    review_time = fields.Float('Review Time')
    interview_time = fields.Float('Interview Time')
    offer_time = fields.Float('Offer Time')
    hired_time = fields.Float('Hired Time')

    def init(self):
        """Time to Hire """
        tools.drop_view_if_exists(self._cr, 'time_to_hire')
        self._cr.execute("""CREATE OR REPLACE VIEW time_to_hire AS (
                                select row_number() OVER () as id,
                                o.applicant_id as applicant_id,
                                o.id as job_opening_id,
                                round(cast(EXTRACT(epoch from ScreenTime)/86400 as numeric),2) as screen_time,
                                round(cast(EXTRACT(epoch from ReviewTime)/86400 as numeric),2) as review_time, 
                                round(cast(EXTRACT(epoch from InterviewTime)/86400 as numeric),2) as interview_time,
                                round(cast(EXTRACT(epoch from  OfferTime)/86400 as numeric),2) as offer_time, 
                                round(cast(EXTRACT(epoch from (o.cur_trk_dt - o.opening_date)/86400 )as numeric),2) as hired_time
        from ( 
        select 
         summ.applicant_id,
         a.name applicant, o.id, 
         o.name, sum(ScreenTime) ScreenTime,
         sum(ReviewTime) ReviewTime,
         sum(InterviewTime) InterviewTime,
         sum(OfferTime) OfferTime,
          o.create_date opening_date,
           max (cur_trk_dt) cur_trk_dt from (
    select 
     calcn.applicant_id,
     case when  old_stage.name = 'Screened' and new_stage.name = 'Shortlisted' then days else  now() - now() end ScreenTime,
     case when  old_stage.name = 'Shortlisted' and new_stage.name = 'Interview' then days else now() - now() end ReviewTime,
     case when  old_stage.name = 'Interview' and new_stage.name = 'Selected' then days else now() - now() end InterviewTime,
     case when  old_stage.name = 'Selected' and new_stage.name = 'Offered' then days else now() - now() end OfferTime,
     cur_trk_dt cur_trk_dt
    from (
        select 
         applicant_id,
         old_stage_id,
         new_stage_id,
         max(days_calc.cur_trk_dt) cur_trk_dt,
         Sum(cur_trk_dt - prv_trk_dt) days 
        from (
                WITH cte AS ( 
                SELECT 
                applicant_id,
                old_stage_id,
                new_stage_id,
                write_date track_date FROM applicant_activity where  old_stage_id < new_stage_id ORDER BY write_date ) 
                SELECT applicant_id,
                old_stage_id,
                new_stage_id,  
                track_date cur_trk_dt,
                 LAG(track_date,1) OVER (PARTITION BY applicant_id  ORDER BY track_date  ) prv_trk_dt 
                FROM cte 
                order by track_date 
            ) days_calc 
            group by applicant_id,
                     old_stage_id,
                     new_stage_id
    )calcn
        join hr_recruitment_stage old_stage on  old_stage.id=calcn.old_stage_id 
        join hr_recruitment_stage new_stage on  new_stage.id=calcn.new_stage_id
    )summ 
    join hr_applicant a on a.id=summ.applicant_id
    join job_opening o on o.id = a.job_opening_id
    join hr_recruitment_stage final_stage on  final_stage.id=a.stage_id
    group by summ.applicant_id,
     a.name,
     o.id,
     o.name) o )""")
