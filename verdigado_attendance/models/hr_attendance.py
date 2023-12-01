# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models

from .hr_attendance_break import DatetimeWithoutSeconds


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in = DatetimeWithoutSeconds()
    check_out = DatetimeWithoutSeconds()

    def _update_overtime(self, employee_attendance_dates=None):
        """Recreate missing overtime records"""
        result = super()._update_overtime(
            employee_attendance_dates=employee_attendance_dates
        )
        if employee_attendance_dates is None:
            employee_attendance_dates = self._get_attendances_dates()
        missing_vals = []
        for employee, attendance_dates in employee_attendance_dates.items():
            dates = [attendance_date for _dummy, attendance_date in attendance_dates]
            existing_overtime = self.env["hr.attendance.overtime"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("company_id", "=", self.env.company.id),
                    ("date", "in", dates),
                ]
            )
            missing_vals += [
                {"employee_id": employee.id, "date": attendance_date}
                for attendance_date in set(dates)
                - set(existing_overtime.mapped("date"))
            ]
        self.env["hr.attendance.overtime"].sudo().create(missing_vals)
        return result
