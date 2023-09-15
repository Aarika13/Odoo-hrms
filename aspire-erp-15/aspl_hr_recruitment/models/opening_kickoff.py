import logging
from datetime import datetime
from odoo import models, fields, api, _
import ast
from ..common.validation import Validation
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta


_logger = logging.getLogger(__name__)


class OpeningKickoff(models.Model):
    _name = 'opening.kickoff'
    _description = 'Opening Kickoff'
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = "name asc"

    name = fields.Char(string='Opening Kick-off', required=True, index=True, translate=True)
    stage_id = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submitted'), ('approve', 'Approved'), ('refuse', 'Refused')], default='draft', string='Status')
    description = fields.Text(string='Job Description',required=True)
    expected_end_date = fields.Date("Expected End Date")
    no_of_recruitment = fields.Integer(string='Expected New Employees', copy=False,
                                       help='Number of new employees you expect to recruit.', default=1,required=True)
    minimum_exp = fields.Integer(string="Minimum Experience Required")
    maximum_exp = fields.Integer(string="Maximum Experience Required") 
    approver = fields.Many2one('res.users', string='Approver',required=True)

    categ_req_ids = fields.Many2many('hr.applicant.category', 'opening_kickoff_categ_req_user_rel', 'job_opening_id',
                                     'user_id', string="Tags") 

    priority = fields.Selection([
        ('0', 'Null'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
    ],required=True)

    opened_date =fields.Date(string="Opened Date",default=datetime.today())

    owner_id = fields.Many2one('res.users', "Owner", tracking=True)
    active = fields.Boolean('Active',default = True)
    approver_true = fields.Boolean("Conditional Approver",compute='get_current_user')
    job_opening_id = fields.Many2one('job.opening','Job Opening')
    available_opening = fields.Boolean("Opening Availability",default = False)

    
    def unlink(self):
        for record in self:
            if record.stage_id == 'submit':
                raise ValidationError(_('Opening kickoff cannot be deleted if the stage is Submitted.'))
            elif record.stage_id == 'approve':
                raise ValidationError(_('Opening kickoff cannot be deleted if the stage is Approved.'))
            elif record.stage_id == 'refuse':
                raise ValidationError(_('Opening kickoff cannot be deleted if the stage is Refused.'))

        return super(OpeningKickoff, self).unlink()

    def get_current_user(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)

        if user.id == self.approver.id:
            self.approver_true = True
        else:
            self.approver_true = False
   
    def submit_button(self):
        self.stage_id = 'submit'

    def approve_button(self):
        self.stage_id = 'approve'

    def draft_button(self):
        self.stage_id = 'draft'    

    def refuse_button(self):
        self.stage_id = 'refuse'

    def create_job_application(self):
        categ_id = self.categ_req_ids.ids
        applicant_data = {
            'default_categ_req_ids':[(6,0,categ_id)],
            'default_name': self.name,
            'default_minimum_exp': self.minimum_exp,
            'default_maximum_exp': self.maximum_exp,
            'default_description': self.description,
            'default_no_of_recruitment': self.no_of_recruitment,
            'default_priority':self.priority,
            'default_owner_id':self.create_uid.id,
            'default_kick_off_id':self.id
            }
        dict_act_window = self.env['ir.actions.act_window']._for_xml_id('aspl_hr_recruitment.action_job_opening_form')
        dict_act_window['context'] = applicant_data
        return dict_act_window
   

    @api.model
    def create(self,vals):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
    
        # job_opening_id = self.env['job.opening'].create({
        #     'name': vals['name'],
        #     'description': vals['description'],
        #     'expected_end_date': vals['expected_end_date'],
        #     'no_of_recruitment': vals['no_of_recruitment'],
        #     'minimum_exp': vals['minimum_exp'],
        #     'maximum_exp': vals['maximum_exp'],
        #     'categ_req_ids': vals['categ_req_ids'],
        #     'priority': vals['priority'],
        #     'opened_date': vals['opened_date'],
        #     'owner_id': user.id,
        #     })
        
        vals['owner_id'] = user.id
        
        result = super(OpeningKickoff,self).create(vals)
        return result

    @api.constrains('opened_date', 'expected_end_date')
    def _check_dates_constraints(self):
        if self.opened_date and self.expected_end_date:
            flag = Validation.check_date(self.opened_date, self.expected_end_date)
            if not flag:
                raise ValidationError("'Expected End Date' must be greater than 'Opened Date' in company history")
        return True




                                    

