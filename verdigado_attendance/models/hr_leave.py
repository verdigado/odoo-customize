# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.depends("employee_id")
    def _compute_from_employee_id(self):
        """Keep the leave type an HR user picked for a new request

        Core clears holiday_status_id whenever employee_id points at somebody
        other than the current user *and* differs from the original record. On
        a new record _origin.employee_id is empty, so that second test is
        always true: the field is cleared on every onchange and the request can
        never be saved via Employee > Time Off > New. Only clear it when there
        really was a previous employee to change away from.

        This reimplements rather than extends the core method: reading
        holiday_status_id before calling super would read a field this very
        method computes. Keep in sync with
        hr_holidays/models/hr_leave.py::_compute_from_employee_id
        """
        for holiday in self:
            holiday.manager_id = holiday.employee_id.parent_id.id
            if (
                holiday.employee_id.user_id != self.env.user
                and holiday._origin.employee_id
                and holiday._origin.employee_id != holiday.employee_id
            ):
                holiday.holiday_status_id = False

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
        self.sudo()._remove_resource_leave()
        self.read([])
        # manipulate cache to make records look like being in state 'confirm' as
        # super only allows it for this and 'refuse'
        for this in self:
            this._cache["state"] = "confirm"
        return super().action_draft()

    def unlink(self):
        """Reset to draft before unlink to clean up dependent objects"""
        self.action_draft()
        return super().unlink()
