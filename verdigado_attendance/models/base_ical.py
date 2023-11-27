# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class BaseIcal(models.Model):
    _inherit = "base.ical"

    show_on_holiday_calendar = fields.Boolean("Show on holiday calendar")
