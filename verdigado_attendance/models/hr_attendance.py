# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models

from .hr_attendance_break import DatetimeWithoutSeconds


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in = DatetimeWithoutSeconds()
    check_out = DatetimeWithoutSeconds()
    apply_holiday_overtime_factor = fields.Boolean()

    def _update_overtime(self, employee_attendance_dates=None):
        """
        Recreate missing overtime records to generate correct expected hours
        Create adjustments for extra overtime by holiday factor
        """
        result = super()._update_overtime(
            employee_attendance_dates=employee_attendance_dates
        )
        if not self.exists():
            return result
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
            for date in dates:
                overtime = existing_overtime.filtered(
                    lambda x: x.date == date and not x.adjustment
                )
                if not overtime:
                    # create overtime record for days where worked hours == expected hours
                    missing_vals += [{"employee_id": employee.id, "date": date}]
                    continue
                holiday_overtime = existing_overtime.filtered(
                    lambda x: x.date == date and x.holiday_overtime_for_overtime_id
                )
                factor = employee._get_effective_holiday_overtime_factor(date)
                if factor != 1 and any(self.mapped("apply_holiday_overtime_factor")):
                    # create or update adjustment record to represent extra holiday overtime
                    duration = overtime.duration * factor - overtime.duration
                    if holiday_overtime:
                        holiday_overtime.sudo().duration = duration
                    else:
                        missing_vals.append(
                            {
                                "employee_id": employee.id,
                                "date": overtime.date,
                                "adjustment": True,
                                "duration": duration,
                                "holiday_overtime_for_overtime_id": overtime.id,
                                "note": _("Extra overtime from holiday factor (%.2f)")
                                % factor,
                            }
                        )
                else:
                    holiday_overtime.sudo().unlink()
        self.env["hr.attendance.overtime"].sudo().create(missing_vals)
        return result

    def write(self, vals):
        """Make super update overtimes if we write the factor flag"""
        if "apply_holiday_overtime_factor" in vals and not {
            "employee_id",
            "check_in",
            "check_out",
        } & set(vals):
            result = True
            for this in self:
                result &= this.write(dict(vals, employee_id=this.employee_id.id))
            return result
        return super().write(vals)
