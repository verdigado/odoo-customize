# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from datetime import datetime, time

import pytz

from odoo import api, fields, models


class HrAttendanceOvertime(models.Model):
    _inherit = "hr.attendance.overtime"

    expected_hours = fields.Float(compute="_compute_expected_hours", store=True)

    @api.depends("date", "employee_id", "duration")
    def _compute_expected_hours(self):
        for this in self:
            employee = this.employee_id
            tz = pytz.timezone(employee.tz)
            this.expected_hours = (
                this.adjustment
                and False
                or employee.with_context(
                    exclude_public_holidays=True,
                    employee_id=employee.id,
                )._get_work_days_data_batch(
                    tz.localize(datetime.combine(this.date, time.min)).astimezone(
                        pytz.utc
                    ),
                    tz.localize(datetime.combine(this.date, time.max)).astimezone(
                        pytz.utc
                    ),
                )[
                    employee.id
                ][
                    "hours"
                ]
            )

    def unlink(self):
        """Exclude adjustments from unlinking if asked"""
        if self.env.context.get("hr_attendance_overtime_unlink_exclude_adjustment"):
            self = self.filtered(lambda x: not x.adjustment)
        return super(HrAttendanceOvertime, self).unlink()
