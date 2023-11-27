# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    def write(self, vals):
        """Don't delete overtime records that are adjustments when changing overtime settings"""
        if "hr_attendance_overtime" in vals or "overtime_start_date" in vals:
            self = self.with_context(
                hr_attendance_overtime_unlink_exclude_adjustment=True
            )
        return super(ResCompany, self).write(vals)
