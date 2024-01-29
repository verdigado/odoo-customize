# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    dashboard_action_id = fields.Many2one("ir.actions.actions")

    def _get_days_request(self):
        """Add a formatted version for every field used in calendar header"""
        result = super()._get_days_request()
        for key in (
            "virtual_leaves_taken",
            "virtual_remaining_leaves",
            "usable_remaining_leaves",
        ):
            if key not in result[1]:
                continue
            if result[1]["request_unit"] == "hour":
                formatted = self.env["ir.qweb.field.float_time"].value_to_html(
                    float(result[1][key]), {}
                )
            else:
                formatted = result[1][key]
            result[1]["%s_formatted" % key] = formatted
        result[1]["dashboard_action_id"] = self.dashboard_action_id.id
        if (
            "usable_remaining_leaves_formatted" in result[1]
            and "virtual_remaining_leaves_formatted" not in result[1]
        ):
            result[1]["virtual_remaining_leaves_formatted"] = result[1][
                "virtual_usable_leaves_formatted"
            ]
        overlap_ids = []
        overlap_time = 0.0
        for overlap1, overlap2, time in self._get_overlap(
            self._get_contextual_employee_id()
        ):
            overlap_ids += overlap1.ids + overlap2.ids
            overlap_time += time
        result[1]["overlap"] = {
            "time": overlap_time,
            "ids": overlap_ids,
        }
        return result

    @api.model
    def get_systray_data(self):
        return self.env.ref(
            "hr_holidays_attendance.holiday_status_extra_hours"
        )._get_days_request()
