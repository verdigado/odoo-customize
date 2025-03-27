from odoo import models, fields

# 1. change constraint for unique_number
class ResPartner(models.Model):
    _inherit = "res.partner"

    x_gliederungsid = fields.Integer(string="Gliederungs-ID")
    x_kunde_hosting = fields.Boolean(string="Hostingkunde")
    x_hauptdomain = fields.Char(string="Hauptdomain", store=True, index=True)
