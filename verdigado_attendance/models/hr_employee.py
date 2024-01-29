# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    custom_holiday_overtime_factor = fields.Boolean(
        help="Use a custom overtime factor for holidays/weekens instead of the company's",
        groups="hr.group_hr_user",
    )
    holiday_overtime_factor = fields.Float(
        default=0,
        help="When activated on holidays/weekends, overtime is multiplied with this factor",
        groups="hr.group_hr_user",
    )
    holiday_overtime_holidays = fields.Boolean(
        string="On Holidays", default=True, groups="hr.group_hr_user"
    )
    holiday_overtime_saturday = fields.Boolean(
        string="On Saturdays", default=True, groups="hr.group_hr_user"
    )
    holiday_overtime_sunday = fields.Boolean(
        string="On Sundays", default=True, groups="hr.group_hr_user"
    )

    def _get_effective_holiday_overtime_factor(self, date=None):
        """Return an employee's effective overtime factor for some date"""
        self.ensure_one()
        self = self.sudo()
        date = (
            date
            or self.env["hr.attendance"]._get_day_start_and_day(
                self,
                fields.Datetime.now(),
            )[1]
        )
        weekday = date.isoweekday()
        return (
            (
                self.custom_holiday_overtime_factor
                and self.holiday_overtime_factor
                or self.company_id.holiday_overtime_factor
            )
            if (
                self.custom_holiday_overtime_factor
                and (
                    self.holiday_overtime_saturday
                    and weekday == 6
                    or self.holiday_overtime_sunday
                    and weekday == 7
                    or self.holiday_overtime_holidays
                    and self.env["hr.holidays.public"].is_public_holiday(date, self.id)
                )
                or (
                    self.company_id.holiday_overtime_saturday
                    and weekday == 6
                    or self.company_id.holiday_overtime_sunday
                    and weekday == 7
                    or self.company_id.holiday_overtime_holidays
                    and self.env["hr.holidays.public"].is_public_holiday(date, self.id)
                )
            )
            else 1
        )

    def _attendance_action_change(self):
        """React to default flag for overtime factor"""
        result = super()._attendance_action_change()
        if "default_apply_holiday_overtime_factor" in self.env.context:
            result.write(
                {
                    "apply_holiday_overtime_factor": self.env.context[
                        "default_apply_holiday_overtime_factor"
                    ],
                }
            )
        return result
