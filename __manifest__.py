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
    'category': 'Other',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/views.xml',
        'views/product_view.xml',
        'views/costumer_view.xml',
        'views/price_view.xml',
        'views/stock_view.xml',
        'security/ir.model.access.csv',

    ],
    'application': True,
    'installable': True,

}
