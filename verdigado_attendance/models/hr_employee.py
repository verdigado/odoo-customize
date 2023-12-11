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
        return (
            (
                self.custom_holiday_overtime_factor
                and self.holiday_overtime_factor
                or self.company_id.holiday_overtime_factor
            )
            if (
                date.isoweekday() >= 6
                or self.env["hr.holidays.public"].is_public_holiday(date, self.id)
            )
            else 1
        )
