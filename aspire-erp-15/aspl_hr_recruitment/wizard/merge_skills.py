from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import timedelta, date
import logging

_logger = logging.getLogger(__name__)

class InvoiceMenu(models.Model):
    _name = "merge.skills"
    _description = "Merge Skills"

    primary_skills = fields.Many2one('hr.skill',string='Primary Skills')
    merge_skills = fields.Many2many('hr.skill',string='Merge Skill', domain="[('id', '!=', primary_skills )]")
                             
    def merge_similar_skills(self):
        fields = self.env['ir.model.fields'].search([('relation','=','hr.skill'),('model_id.name','not in',('Merge Skills','Skill Type'))])
        
        for field in fields:
            for skills in self.merge_skills:
                records = self.env[field.model_id.model].search([(field.name,'=',skills.id)])
                for record in records:
                    
                    if 'employee_id' in self.env[str(record).split('(')[0]]._fields: 
                        if self.primary_skills in record.employee_id.employee_skill_ids.skill_id:
                           record.unlink()
                        else:
                            record.write({'skill_id':self.primary_skills.id})

                    elif 'applicant_id' in self.env[str(record).split('(')[0]]._fields:
                        if self.primary_skills in record.applicant_id.applicant_skill_ids.skill_id:
                           record.unlink()
                        else:
                            record.write({'skill_id':self.primary_skills.id})

                    elif 'job_opening_id' in self.env[str(record).split('(')[0]]._fields:
                        if self.primary_skills in record.job_opening_id.opening_skill_ids.skill_id:
                           record.unlink()
                        else:
                            record.write({'skill_id':self.primary_skills.id})

                    elif 'int_feed_id' in self.env[str(record).split('(')[0]]._fields:
                        if self.primary_skills in record.int_feed_id.feedbacks_skill_ids.skill_id:
                           record.unlink()
                        else:
                            record.write({'skill_id':self.primary_skills.id})
                     
                    elif 'candidate_id' in self.env[str(record).split('(')[0]]._fields:
                        if self.primary_skills in record.candidate_id.candidate_skill_ids.skill_id:
                           record.unlink()
                        else:
                            record.write({'skill_id':self.primary_skills.id})

        self.merge_skills.unlink()          
        
