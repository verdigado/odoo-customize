# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    holiday_overtime_factor = fields.Float(
        related="company_id.holiday_overtime_factor", readonly=False
    )
