
from odoo import models, fields, api

class VerdigadoDomain(models.Model):
    _name = "verdigado.domain"
    _description = "Domain specific fields"
    _order = "domain_name"

    domain_id = fields.Many2one("verdigado.domain", string="Domain")
    domain_name = fields.Char(readonly=False)

    active = fields.Boolean(default=True)
    is_main = fields.Boolean(string="Main domain")
    is_list = fields.Boolean(string="Mailinglist domain")
    is_extern = fields.Boolean(string="Domain is managed by customer.")
    start = fields.Date()
    end = fields.Date()
    notes = fields.Text()

    mailboxes_booked = fields.Integer()
    mailboxes_used = fields.Integer(readonly=True)

    lists_booked = fields.Integer()
    lists_used = fields.Integer(readonly=True)

    partner_id = fields.Many2one("res.partner", "Partner", readonly=True)

    _sql_constraints = [
        ("unique_domain", "unique(domain_name, active)", "Domain must be unique")
    ]
