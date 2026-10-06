# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    show_negative = fields.Boolean("Show zero and negative balances in dashboard")
    dashboard_action_id = fields.Many2one("ir.actions.actions")

    def _get_days_request(self):
        """Add a formatted version for every field used in calendar header"""
        result = super()._get_days_request()
        for key in (
            "virtual_leaves_taken",
            "virtual_remaining_leaves",
            "usable_remaining_leaves",
        ):
            if key not in result[1]:
                continue
            if result[1]["request_unit"] == "hour":
                formatted = self.env["ir.qweb.field.float_time"].value_to_html(
                    float(result[1][key]), {}
                )
            else:
                formatted = result[1][key]
            result[1]["%s_formatted" % key] = formatted
        result[1]["dashboard_action_id"] = self.dashboard_action_id.id
        if (
            "usable_remaining_leaves_formatted" in result[1]
            and "virtual_remaining_leaves_formatted" not in result[1]
        ):
            result[1]["virtual_remaining_leaves_formatted"] = result[1][
                "virtual_usable_leaves_formatted"
            ]
        overlap_ids = []
        overlap_time = 0.0
        for overlap1, overlap2, time in self._get_overlap(
            self._get_contextual_employee_id(), leave_type=self.id
        ):
            overlap_ids += overlap1.ids + overlap2.ids
            overlap_time += time

        result[1]["overlap"] = {
            "time": round(overlap_time, 2),
            "ids": overlap_ids,
        }
        result[1]["per_year"] = self._get_days_per_year()

        return result

    def _get_days_per_year(self):
        """Break down entitlement and usage per allocation year

        The dashboard only shows a single aggregated number, which is hard to
        follow because allocations stay valid until March 31st of the following
        year. Between January and March two allocations are therefore valid at
        the same time and both feed into that number.

        Every allocation year is reported, including expired ones. Credit
        allocations from overlaps show up as entitlement of the year the days
        were lost in. The leaves hr_holidays could not charge to any allocation
        are deliberately left out, see the comment at the end of this method.
        """
        self.ensure_one()
        employee_id = self._get_contextual_employee_id()
        # in the employee dashboard the context carries a list of ids, passing
        # that on unchanged builds an "employee_id in (ARRAY[...])" query and
        # makes postgres fail. _get_overlap above guards against the same thing.
        if isinstance(employee_id, (list, tuple)):
            employee_id = employee_id[0] if employee_id else False
        if not employee_id:
            return []
        days_per_allocation = self._get_employees_days_per_allocation([employee_id])
        allocation_days = days_per_allocation[employee_id][self]
        today = fields.Date.context_today(self)
        per_year = {}
        for allocation, days in allocation_days.items():
            # False and "error" are buckets for leaves without a valid
            # allocation, they have no year to report
            if not allocation or isinstance(allocation, str):
                continue
            entry = per_year.setdefault(
                allocation.date_from.year,
                {
                    "max_leaves": 0.0,
                    "leaves_taken": 0.0,
                    "expired": 0.0,
                    "allocations": self.env["hr.leave.allocation"],
                },
            )
            entry["allocations"] |= allocation
            # days["max_leaves"] is only filled in for allocations that are
            # still valid today, so an expired allocation of the previous year
            # would report an entitlement of 0. Read it off the allocation
            # itself instead, the same way hr_holidays does.
            entitlement = (
                allocation.number_of_days
                if allocation.type_request_unit in ("day", "half_day")
                else allocation.number_of_hours_display
            )
            entry["max_leaves"] += entitlement
            entry["leaves_taken"] += days["virtual_leaves_taken"]
            # whatever was left when an allocation ran out of validity is gone.
            # Without this the rows read like there was still a balance left.
            if allocation.date_to and allocation.date_to < today:
                entry["expired"] += max(entitlement - days["virtual_leaves_taken"], 0.0)
        result = []
        for year in sorted(per_year):
            entry = per_year[year]
            allocations = entry["allocations"]
            # hr.leave.holiday_allocation_id is deprecated in 15.0 and always
            # computed to False, so there is no stored link between a leave and
            # the allocation it was charged to. Matching on the validity window
            # is the next best thing, and it has to match on the *start* of the
            # leave: one that began in the previous year was charged to the
            # previous year's allocation even when it ran into this one.
            # What stays ambiguous are leaves starting between January and
            # March, where two allocations are valid at the same time.
            domain = [
                ("employee_id", "=", employee_id),
                ("holiday_status_id", "=", self.id),
                ("state", "in", ["confirm", "validate1", "validate"]),
                (
                    "date_from",
                    ">=",
                    "%s 00:00:00" % min(allocations.mapped("date_from")),
                ),
            ]
            # credit allocations from overlaps have no end date by design, so
            # they must not widen the window the leaves are looked up in
            dates_to = allocations.filtered(
                lambda x: not x.overlap_sick_leave_id
            ).mapped("date_to")
            if dates_to and all(dates_to):
                domain.append(("date_from", "<=", "%s 23:59:59" % max(dates_to)))
            result.append(
                {
                    "year": year,
                    "max_leaves": round(entry["max_leaves"], 2),
                    "leaves_taken": round(entry["leaves_taken"], 2),
                    "expired": round(entry["expired"], 2),
                    "domain": domain,
                    # tooltip on the link, spells out which year the listed
                    # leaves belong to
                    "taken_label": _("taken in %s") % year,
                }
            )
        # The leaves hr_holidays could not charge to any allocation are
        # deliberately not listed here: the figure needs so much context that it
        # confused more than it explained. It is still in the False bucket of
        # _get_employees_days_per_allocation if it is ever needed again.
        return result

    @api.model
    def get_systray_data(self):
        return self.env.ref(
            "hr_holidays_attendance.holiday_status_extra_hours"
        )._get_days_request()

    # overwrites method in hr_holidays
    @api.model
    def get_days_all_request(self):
        # apply for extra hours time off type as well
        extra_hours_time_off_type = self.env.ref(
            "hr_holidays_attendance.holiday_status_extra_hours",
            raise_if_not_found=False,
        )

        # apply for default paid leave type as well
        holiday_status_cl = self.env.ref(
            "hr_holidays.holiday_status_cl",
            raise_if_not_found=False,
        )

        leave_types = self.search([]).filtered(
            lambda x: x.virtual_remaining_leaves > 0
            or x.max_leaves
            or x.show_negative
            or (x == holiday_status_cl)
            or (x == extra_hours_time_off_type)
        )

        leave_types = sorted(
            leave_types,
            key=self._model_sorting_key,
            reverse=True,
        )

        return [lt._get_days_request() for lt in leave_types]
