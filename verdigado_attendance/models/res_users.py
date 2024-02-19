# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def get_effective_holiday_overtime_factor(self):
        if self.env.user.employee_id:
            return self.env.user.employee_id._get_effective_holiday_overtime_factor()
        else:
            return 1.0
