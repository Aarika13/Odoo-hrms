from odoo import api,fields, models

class ProjecttTags(models.Model):
    _name = "projectt.tags"
    _description = "Projectt Tags"
    _rec_name = 'tags'

    tags = fields.Char(string = "Tags")
    
# ********** SQL CONSTRAINTS ************ #
    _sql_constraints = [
        ('unique_tags' , 'unique(tags)' , 'Tag-Name Must be a Unique !')
    ]