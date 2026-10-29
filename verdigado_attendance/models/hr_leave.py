# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

import pytz

from odoo import api, fields, models

from odoo.addons.resource.models.resource import float_to_time


class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.depends(
        "request_date_from_period",
        "request_hour_from",
        "request_hour_to",
        "request_date_from",
        "request_date_to",
        "request_unit_half",
        "request_unit_hours",
        "request_unit_custom",
        "employee_id",
    )
    def _compute_date_from_to(self):
        """Pin the times to the working hours valid on the requested dates

        The depends above repeats the one in hr_holidays. It has to: Odoo
        reads the dependencies of a computed field off the last compute in the
        inheritance chain, so leaving it out here would strip date_from and
        date_to of every dependency and they would never recompute at all.
        Keep in sync with hr_holidays/models/hr_leave.py::_compute_date_from_to

        Core reads the attendances of the employee's calendar without looking
        at their validity period. It groups them by weekday and day period and
        takes min(hour_from) and max(hour_to) across all of them. That is
        harmless for a plain calendar, but hr_employee_calendar_planning keeps
        the whole history of an employee in one calendar as dated attendance
        lines, and then an expired line decides when a leave begins or ends: an
        afternoon block that stopped at 15:00 two years ago still outranks
        today's single block running until 16:42.

        Only an end that is too early costs anything, since the overlap with
        the working hours caps the other direction. But it does so quietly, as
        a fraction of a day that nobody notices.

        Correct the two timestamps afterwards instead of reimplementing the
        core method, which also covers half days, hour requests and two week
        calendars and would have to be kept in sync with every upgrade.
        """
        result = super()._compute_date_from_to()
        for leave in self:
            leave._align_dates_with_valid_attendances()
        return result

    def _get_attendances(self, employee, request_date_from, request_date_to):
        """Narrow the grouping to the attendances valid in that period

        This is the second place where hr_holidays decides a leave's times,
        and the one default_get uses - so it is what the calendar view and
        the form actually go through. Its domain ignores the validity of the
        attendance lines just like _compute_date_from_to does.

        The window is passed down through the context and applied in
        resource_calendar_attendance.py, which keeps the core logic itself
        untouched.
        """
        return super(
            HrLeave,
            self.with_context(
                hr_leave_attendances_valid_on=(request_date_from, request_date_to)
            ),
        )._get_attendances(employee, request_date_from, request_date_to)

    def _align_dates_with_valid_attendances(self):
        target = self._valid_attendance_dates()
        if target:
            self.date_from, self.date_to = target

    def _valid_attendance_dates(self):
        """The times this leave should carry, or None if we are not in charge

        Earliest start and latest end of the attendances valid on the
        requested dates, as UTC timestamps.
        """
        self.ensure_one()
        if not self.date_from or not self.date_to:
            return None
        if not self.request_date_from or not self.request_date_to:
            return None
        # these carry the times whoever filed the request picked, leave them be
        if self.request_unit_half or self.request_unit_hours:
            return None
        if getattr(self, "request_unit_custom", False):
            return None
        calendar = self.employee_id.resource_calendar_id
        # core picks attendances per week type for those, too involved to
        # second guess without a case to test it against
        if not calendar or calendar.two_weeks_calendar:
            return None
        starts = self._attendances_valid_on(calendar, self.request_date_from)
        ends = self._attendances_valid_on(calendar, self.request_date_to)
        # a request starting or ending on a day off stays with core, which
        # moves on to the next resp. back to the previous working day
        if not starts or not ends:
            return None
        tz = pytz.timezone(self.employee_id.tz or calendar.tz or "UTC")
        return (
            self._to_utc(tz, self.request_date_from, min(starts.mapped("hour_from"))),
            self._to_utc(tz, self.request_date_to, max(ends.mapped("hour_to"))),
        )

    @api.model
    def _attendances_valid_on(self, calendar, day):
        """Attendances of that weekday whose validity period covers the day"""
        return calendar.attendance_ids.filtered(
            lambda a: not a.display_type
            and a.dayofweek == str(day.weekday())
            and (not a.date_from or a.date_from <= day)
            and (not a.date_to or a.date_to >= day)
        )

    @api.model
    def _to_utc(self, tz, day, hour):
        return (
            tz.localize(datetime.combine(day, float_to_time(hour)))
            .astimezone(pytz.utc)
            .replace(tzinfo=None)
        )

    @api.model_create_multi
    def create(self, vals_list):
        leaves = super().create(vals_list)
        leaves._align_stored_dates()
        return leaves

    def write(self, values):
        result = super().write(values)
        if "date_from" in values or "date_to" in values:
            self._align_stored_dates()
        return result

    def _align_stored_dates(self):
        """Apply the correction to records, not only through the compute

        The form sends date_from and date_to itself, and the calendar view
        even puts them into the context as defaults. A field that arrives
        with a value is not computed, so _compute_date_from_to - and with it
        _align_dates_with_valid_attendances - never runs for anything created
        or edited through the interface. Measured on 2026-10-28: the module
        was loaded, the compute was called zero times.

        Approved leaves are left alone on purpose. A validated leave blocks
        its own working time through resource.calendar.leaves, and rewriting
        its dates recomputes number_of_days against a calendar it has already
        taken off itself - which lands at zero days.
        """
        if self.env.context.get("hr_leave_aligning"):
            return
        for leave in self:
            target = leave._valid_attendance_dates()
            if leave.state in ("validate", "validate1"):
                continue
            if not target or (leave.date_from, leave.date_to) == target:
                continue
            leave.with_context(hr_leave_aligning=True).write(
                {"date_from": target[0], "date_to": target[1]}
            )

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
