# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import _, api, models
from odoo.tools import float_compare

exclude_sentinel = object()

# A change to any of these can add, remove or resize an overlap, so the
# credit allocations of the employee have to be rebuilt afterwards.
OVERLAP_CREDIT_TRIGGERS = {
    "date_from",
    "date_to",
    "employee_id",
    "holiday_status_id",
    "number_of_days",
    "state",
}


class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.constrains("date_from", "date_to", "employee_id")
    def _check_date(self):
        """Allow overlapping if the holiday type allows it"""
        return super(
            HrLeave,
            self.with_context(hr_holidays_overlap_exclude=exclude_sentinel).filtered(
                lambda x: not x.holiday_status_id.can_overlap
            ),
        )._check_date()

    @api.model
    def search_count(self, args):
        """Inject condition to exclude leaves whose type allows overlaps if asked so"""
        if self.env.context.get("hr_holidays_overlap_exclude") == exclude_sentinel:
            args += [("holiday_status_id.can_overlap", "=", False)]
        return super().search_count(args)

    def _get_leaves_on_public_holiday(self):
        """Don't count leaves with a type that allows overlap"""
        return (
            super()
            ._get_leaves_on_public_holiday()
            .filtered(lambda x: not x.holiday_status_id.can_overlap)
        )

    @api.model_create_multi
    def create(self, vals_list):
        leaves = super().create(vals_list)
        leaves._sync_overlap_credit_allocations()
        return leaves

    def write(self, vals):
        result = super().write(vals)
        if not OVERLAP_CREDIT_TRIGGERS.isdisjoint(vals):
            self._sync_overlap_credit_allocations()
        return result

    def unlink(self):
        employees = self.mapped("employee_id")
        result = super().unlink()
        self._sync_overlap_credits_for_employees(employees)
        return result

    def _sync_overlap_credit_allocations(self):
        """Rebuild the credit allocations of everybody affected by these leaves"""
        self._sync_overlap_credits_for_employees(self.mapped("employee_id"))

    @api.model
    def _sync_overlap_credits_for_employees(self, employees):
        """Reconcile the credit allocations of these employees with the overlaps.

        The credits are derived data: every overlap of a leave whose type allows
        it with a regular leave is mirrored by one allocation, so that the core
        consumption logic sees the days at the time they were lost instead of
        having the balance patched afterwards.
        """
        if not employees or self.env.context.get("hr_holidays_overlap_syncing"):
            return
        this = self.with_context(hr_holidays_overlap_syncing=True)
        Allocation = this.env["hr.leave.allocation"].sudo()
        leave_types = (
            this.env["hr.leave.type"]
            .sudo()
            .search([("can_overlap", "=", False), ("requires_allocation", "=", "yes")])
        )
        for employee in employees:
            existing = Allocation.search(
                [
                    ("employee_id", "=", employee.id),
                    ("overlap_sick_leave_id", "!=", False),
                ]
            )
            by_pair = {
                (a.overlap_sick_leave_id.id, a.overlap_leave_id.id): a for a in existing
            }
            keep = Allocation.browse()
            for leave_type in leave_types:
                for sick_leave, leave, days in leave_type._get_overlap(
                    employee.id, leave_type.id
                ):
                    if float_compare(days, 0, precision_digits=2) <= 0:
                        continue
                    allocation = by_pair.get((sick_leave.id, leave.id))
                    if allocation:
                        values = {}
                        if float_compare(
                            allocation.number_of_days, days, precision_digits=2
                        ):
                            values["number_of_days"] = days
                        # a credit refused earlier is revived, not duplicated
                        if allocation.state != "validate":
                            values["state"] = "validate"
                        if values:
                            allocation.write(values)
                    else:
                        allocation = Allocation.create(
                            this._overlap_credit_allocation_values(
                                employee, leave_type, sick_leave, leave, days
                            )
                        )
                    keep |= allocation
            # Credits that lost their overlap are refused rather than deleted:
            # hr_holidays forbids deleting an allocation that is validated or
            # already has leaves charged to it. Only allocations in state
            # validate count towards the balance, and archiving would not help
            # because they are read with active_test=False.
            obsolete = (existing - keep).filtered(lambda x: x.state != "refuse")
            if obsolete:
                obsolete.write({"state": "refuse"})

    @api.model
    def _overlap_credit_allocation_values(
        self, employee, leave_type, sick_leave, leave, days
    ):
        """Values of the allocation crediting back one overlapped leave"""
        return {
            "name": _("Overlap credit: %s", leave.display_name),
            "holiday_status_id": leave_type.id,
            "employee_id": employee.id,
            "holiday_type": "employee",
            "allocation_type": "regular",
            "number_of_days": days,
            # Valid from the day the credited leave started, so it can cover
            # that leave itself, and without an end date, so it does not expire
            # along with the allocation the days were originally taken from.
            # Odoo consumes allocations without an end date last.
            "date_from": leave.date_from.date(),
            "date_to": False,
            "state": "validate",
            "overlap_sick_leave_id": sick_leave.id,
            "overlap_leave_id": leave.id,
        }
