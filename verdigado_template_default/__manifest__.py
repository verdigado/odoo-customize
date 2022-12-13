# -*- coding: utf-8 -*-
{
    'name': "Verdigado Standard Templates",

    'description': """
        Die Verdigado Standard Templates
    """,

    'author': "verdigado eG",
    'website': "https://www.verdigado.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Customizations',
    'version': '0.3',

    "license": "LGPL-3",
    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'l10n_de', 'account_sepa_direct_debit', 'website', 'sale_order_line_sequence' ],

    # always loaded
    'data': [
     #   'security/ir.model.access.csv',
        'views/debrand_web.xml',
        #'views/debrand_mail.xml',
        'views/sepa_invoice.xml',
        'views/order_line_number.xml',
        'views/verdigado.xml',
        'views/account_invoices_order.xml',
    ],
    "assets":
    {
        'web._assets_primary_variables': [
            'verdigado_template_default/static/src/scss/primary_variables.scss',
        ],
        'web.assets_frontend': [
           'verdigado_template_default/static/src/scss/verdigado_style.scss',
        ],
        'web.assets_backend': [
            'verdigado_template_default/static/src/scss/ui.scss',
        ],
    },
    'images': [
        'static/src/img/head1.jpg',
    ],
    "installable": True,
}
