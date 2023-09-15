import logging
from odoo import models, fields, api, _
from datetime import date

_logger = logging.getLogger(__name__)

CURRENT_DOCUMENTS = [
    ('appointment', 'Appointment'),
    ('appraisal', 'Appraisal'),
    ('confirmation', 'Confirmation'),
    ('nomination','Nomination'),
    ('exitForm', 'Exit Form'),
    ('experience', 'Experience'),
    ('offer', 'Offer'),
    ('paySlip', 'Pay Slip'),
    ('relieving', 'Relieving'),
    ('other', 'Other'),
]


# Employee family information
class EmployeeDocument(models.Model):
    _name = "employee.document"
    _description = "Employee Document"

    employee_id = fields.Many2one('hr.employee', 'Employee')
    document_name = fields.Char('Attachment Name', required=True)
    document_type = fields.Selection([
        ('pdf', 'PDF'),
        ('word', 'Word'),
        ('other', 'Other'),
    ], 'Document Type', required=True)
    document_description = fields.Text('Description')
    document = fields.Binary('Document', required=True)
    attached_date = fields.Date('Attached Date', default=fields.Date.context_today)
    type = fields.Selection(string='Type',
                            selection=[('past', 'Previous employment'),
                                       ('current', 'Current employment'),
                                       ('education', 'Education'),
                                       ],
                            required=True)
    doc = fields.Selection(CURRENT_DOCUMENTS, 'Document', required=True)


class DocumentType(models.Model):
    _name = "document.type"
    _description = "Document Type"
    _rec_name = 'document_type'

    document_type = fields.Char('Document Type', required=True)
