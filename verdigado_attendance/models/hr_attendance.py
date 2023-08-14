# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

#
# dummy model to allow verdigado_hr_attendance_rule_attendance_manager rule
#

from odoo import models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    def _update_overtime(self, employee_attendance_dates=None):
        """Set the flag in context to exclude public holidays"""
        # TODO move this to glue module hr_holidays_public_attendance
        return super(
            HrAttendance, self.with_context(exclude_public_holidays=True)
        )._update_overtime(employee_attendance_dates=employee_attendance_dates)
