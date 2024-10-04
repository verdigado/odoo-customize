from odoo import models, fields

# 1. change constraint for unique_number
class ResPartner(models.Model):
    _inherit = "res.partner"

    x_gliederungsid = fields.Integer()
    x_kunde_hosting = fields.Boolean()
    x_hauptdomain = fields.Char(string="Hauptdomain", store=True, index=True)
