# Copyright 2022 verdigado eG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Verdigado Standard Templates",
    "author": "verdigado eG",
    "website": "https://github.com/verdigado/odoo-customize",
    "category": "Customizations",
    "version": "16.0.0.1.0",
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
    ],
    "data": [
        "views/debrand_web.xml",
        "views/debrand_mail.xml",
        "views/res_partner.xml",
        # "views/order_line_number.xml",
        "views/report_invoice.xml",
        "views/sepa_invoice.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            "verdigado_template_default/static/src/scss/primary_variables.scss",
        ],
        "web.assets_frontend": [
            "verdigado_template_default/static/src/scss/verdigado_style.scss",
            "verdigado_template_default/static/src/scss/ui.scss",
        ],
        "web.assets_backend": [
            "verdigado_template_default/static/src/scss/web_backend.scss"
        ],
        "web.assets_common": ["verdigado_template_default/static/src/scss/ui.scss"],
        "web.report_assets_common": [
            "verdigado_template_default/static/src/scss/report_assets.scss"
        ],
    },
    "images": [
        "static/src/img/head1.jpg",
    ],
    "installable": True,
}
