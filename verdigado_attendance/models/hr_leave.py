# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def _check_approval_update(self, state):
        """Always allow to reset to draft for future leaves"""
        if state == "draft":
            self = self.filtered(
                lambda x: not x.date_from
                or x.date_from.date() <= fields.Date.today()
                and self.env.user.employee_id
                not in (x.manager_id | x.employee_id.leave_manager_id.employee_id)
            )
        return super(HrLeave, self)._check_approval_update(state)

    def action_draft(self):
        """Allow setting to draft from any state"""
        # manipulate cache to make records look like being in state 'confirm' as
        # super only allows it for this and 'refuse'
        self.read([])
        for this in self:
            this._cache["state"] = "confirm"
        return super().action_draft()

    def unlink(self):
        """Reset to draft before unlink to clean up dependent objects"""
        self.action_draft()
        return super().unlink()
