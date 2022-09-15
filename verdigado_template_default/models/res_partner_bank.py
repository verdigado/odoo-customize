# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    # apply patch https://github.com/odoo/odoo/pull/15637/files for verdigado
    _sql_constraints = [
        ('unique_number', 'unique(sanitized_acc_number, company_id, partner_id)', 'Account Number must be unique'),
    ]
