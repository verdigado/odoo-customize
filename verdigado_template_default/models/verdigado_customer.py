# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    hosting_customer = fields.Boolean()

    domain_ids = fields.One2many(
        comodel_name="verdigado.domain",
        inverse_name="partner_id",
        string="Domains",
        copy=True,
    )

    # domain_ids = fields.Many2many("verdigado.domain", "res_partner_domain_rel", "partner_id",
    #                               "domain_id", string="Domain List")
