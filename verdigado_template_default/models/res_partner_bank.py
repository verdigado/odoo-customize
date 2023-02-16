# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# make IBAN unique for single partner - not for whole company

# 1. change constraint for unique_number
class ResPartnerBank(models.Model):

    _inherit = "res.partner.bank"

    # apply patch https://github.com/odoo/odoo/pull/15637/files for verdigado
    _sql_constraints = [
        ('unique_number', 'unique(sanitized_acc_number, company_id, partner_id)', 'Account Number must be unique'),
    ]

# 1. change method for bank reconciliation
class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    def _find_or_create_bank_account(self):
        if self.company_id.country_id.code == 'DE':
            bank_account = self.env['res.partner.bank'].search(
                [('company_id', '=', self.company_id.id),
                 ('acc_number', '=', self.account_number),
                 ('partner_id', '=', self.partner_id.id)])
            return bank_account
        else:
            super(AccountBankStatementLine, self)._find_or_create_bank_account()
