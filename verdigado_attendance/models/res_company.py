# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    holiday_overtime_factor = fields.Float(
        default=1,
        help="When activated on holidays/weekends, overtime is multiplied with this factor",
    )
    holiday_overtime_holidays = fields.Boolean(string="Holidays", default=True)
    holiday_overtime_saturday = fields.Boolean(string="Saturdays", default=True)
    holiday_overtime_sunday = fields.Boolean(string="Sundays", default=True)

    def write(self, vals):
        """Don't delete overtime records that are adjustments when changing overtime settings"""
        if "hr_attendance_overtime" in vals or "overtime_start_date" in vals:
            self = self.with_context(
                hr_attendance_overtime_unlink_exclude_adjustment=True
            )
        return super(ResCompany, self).write(vals)
