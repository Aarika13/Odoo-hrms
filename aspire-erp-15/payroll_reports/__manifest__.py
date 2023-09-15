{
    'name': 'Payroll Reports',
    'version': '1.0.0',
    'category': '',
    'sequence': -1,
    'author': 'Manthan',
    'summary': 'Custom Payroll Reports',
    'description': """Payroll Reports of aspl employees""",
    'depends': ['hr_payroll_community','hr'],
    'data': [
        'reports/report.xml',
        'reports/template.xml',
    ],
    'demo': [],
    # 'application': True,
    'installable': True,
    'license': 'LGPL-3',
}