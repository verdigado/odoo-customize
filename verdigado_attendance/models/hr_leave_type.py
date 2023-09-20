# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    dashboard_action_id = fields.Many2one("ir.actions.actions")

    def _get_days_request(self):
        """Add a formatted version for every field used in calendar header"""
        result = super()._get_days_request()
        for key in ("virtual_leaves_taken", "virtual_remaining_leaves"):
            if result[1]["request_unit"] == "hour":
                formatted = self.env["ir.qweb.field.float_time"].value_to_html(
                    float(result[1][key]), {}
                )
            else:
                formatted = result[1][key]
            result[1]["%s_formatted" % key] = formatted
        result[1]["dashboard_action_id"] = self.dashboard_action_id.id
        return result

    @api.model
    def get_systray_data(self):
        return self.env.ref(
            "hr_holidays_attendance.holiday_status_extra_hours"
        )._get_days_request()
