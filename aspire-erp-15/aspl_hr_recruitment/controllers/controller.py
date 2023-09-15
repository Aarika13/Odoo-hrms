# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class CandidateFeedbackController(http.Controller):

    @http.route('/feedback/<self_id>', type="http", auth="public", website=True)
    def create_feedback(self, self_id, **kw):
        applicant_obj = request.env['hr.applicant'].sudo().search([('id', '=', self_id)])
        result = {}
        for que_ans in applicant_obj:
            res = {
                'que1': que_ans.que1,
                'que2': que_ans.que2,
                'que3': que_ans.que3,
                'que4': que_ans.que4,
                'que5': que_ans.que5,
            }
            result = res
            break
        if request.httprequest.method == 'POST':
            applicant_obj.sudo().write({
                'rating1': kw['rating1'],
                'rating2': kw['rating2'],
                'rating3': kw['rating3'],
                'rating4': kw['rating4'],
                'rating5': kw['rating5'],
            })
            applicant_obj.feedback_status = True
            # total = int(applicant_obj.rating1) + int(applicant_obj.rating2) + int(applicant_obj.rating3) + int(
            #     applicant_obj.rating4) + int(applicant_obj.rating5)
            # applicant_obj.feedback_average = total / 5
            return request.render("aspl_hr_recruitment.candidate_thanks")
        else:
            if not applicant_obj.feedback_status:
                return request.render("aspl_hr_recruitment.create_feedback", result)
            else:
                return request.render("aspl_hr_recruitment.already_submitted")
