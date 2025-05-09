# Copyright 2022 verdigado eG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Verdigado Standard Templates",
    'description': """
verdigado-Layout für odoo
=============================================
""",
    "author": "verdigado eG",
    "website": "https://github.com/verdigado/odoo-customize",
    "category": "Customizations",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "account",
        "l10n_de",
        "account_sepa_direct_debit",
        "website",
        # "sale_order_line_sequence",
        "module_auto_update",
        "auth_oidc"
    ],
    "data": [
        "views/debrand_web.xml",
        "views/debrand_mail.xml",
        "views/res_partner.xml",
        # "views/order_line_number.xml",
        # "views/report_invoice.xml",
        # "views/sepa_invoice.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "verdigado_template_default/static/src/scss/home_menu_background.scss", # used by login page
            "verdigado_template_default/static/src/scss/verdigado_style.scss",
        ],
        "web._assets_primary_variables": [
            "verdigado_template_default/static/src/scss/primary_variables.scss",
        ],
        "web.assets_backend": [
            "verdigado_template_default/static/src/scss/home_menu_background.scss"
        ],
        # "web.report_assets_common": [
        #     "verdigado_template_default/static/src/scss/report_assets.scss"
        # ],
    },
    "images": [
        "static/src/img/head1.jpg",
    ],
    "installable": True,
}
