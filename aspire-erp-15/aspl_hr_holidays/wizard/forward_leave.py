# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ForwardLeave(models.TransientModel):
    _name = 'forward.leave'
    _description = "Forward Leave"

    forward_to = fields.Many2one('hr.employee', 'Employee', domain=[('with_organization', '=', True)])
    comment = fields.Text("Comment")
    leave_id = fields.Many2one('hr.leave', "Leave Id")

    def forward(self):
        current_leave_id = self.env.context.get('active_id')
        if current_leave_id:
            # self.env['hr.leave'].write(context['leave_id'],
            #                                    {'forward_to': forward_leave_data.forward_to.id}, context=None)
            # forward_leave_obj.write(cr, uid, ids, {'leave_id': context['leave_id']}, context=None)
            # holy_obj = self.pool.get('hr.leave').browse(cr, uid, context['leave_id'], context=None)
            # from_emp_obj = self.pool.get('res.users').browse(cr, uid, uid, context=None)
            #
            # message = _("<p> Leave request forwarded <br> From: %s  <br> To: %s <br> Note: %s </p>") % (
            #     holy_obj.forward_to.name, from_emp_obj.name, str(forward_leave_data.comment))
            #
            # self.env['hr.leave'].message_post(cr, uid, context['leave_id'],
            #                                       body=message, context=None)
            # self.env['hr.leave.allocation'].write({
            #     'forward_to': self.forward_to.id,
            #     'holiday_status_id': self.forward_to.id
            # })
            self.env['hr.leave'].write({
                'forward_to': self.forward_to.id,
                'holiday_status_id': current_leave_id
            })

