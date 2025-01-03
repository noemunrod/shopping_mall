# -*- coding: utf-8 -*-
{
    'name': "shopping_mall",

    'summary': """
        Odoo module based in a real life backend shopping mall interactions""",

    'description': """
        Odoo module based in real life backend shopping mall interactions
    """,

    'author': "noemunrod",
    'website': "https://www.linkedin.com/in/nomudev/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Shopping',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/hr.xml',
        'report/event_report.xml',

    ],
    'installable': True,
    'application': True,
}
