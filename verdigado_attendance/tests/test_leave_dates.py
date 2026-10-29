# Copyright 2026 verdigado eG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase

# both Fridays, well after the calendar switch below
FRIDAY = "2026-06-05"
OTHER_FRIDAY = "2026-06-12"
# Europe/Berlin is UTC+2 in June
EXPECTED_FROM = "2026-06-05 07:00:00"  # 09:00 local
EXPECTED_TO = "2026-06-05 14:00:00"  # 16:00 local


class TestLeaveDates(TransactionCase):
    """Leave times must follow the attendances valid on the requested dates.

    The calendar built here is the shape hr_employee_calendar_planning
    produces for somebody whose schedule changed: the old plan stays behind as
    dated attendance lines next to the current one. Core groups all of them by
    weekday and day period without looking at the validity, so the expired
    afternoon line would end the leave at 15:00 and the expired morning line
    would start it at 08:00.

    Everything is built from scratch, the demo data this module's other tests
    rely on is dated relative to today and does not install.
    """

    def _calendar(self, name, blocks):
        """blocks: list of (hour_from, hour_to, day_period) for Mon to Fri"""
        return self.env["resource.calendar"].create(
            {
                "name": name,
                "tz": "Europe/Berlin",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "%s %s" % (name, period),
                            "dayofweek": str(day),
                            "hour_from": hour_from,
                            "hour_to": hour_to,
                            "day_period": period,
                        },
                    )
                    for day in range(5)
                    for hour_from, hour_to, period in blocks
                ],
            }
        )

    def setUp(self):
        super().setUp()
        # The dated attendance lines are not built by hand: that is what
        # hr_employee_calendar_planning does out of the planning lines below,
        # and its create would overwrite a calendar set directly anyway.
        old_plan = self._calendar(
            "Alter Plan", [(8.0, 12.0, "morning"), (12.5, 15.0, "afternoon")]
        )
        new_plan = self._calendar("Neuer Plan", [(9.0, 16.0, "morning")])
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Umgestellt Tester",
                "tz": "Europe/Berlin",
                "calendar_ids": [
                    (
                        0,
                        0,
                        {
                            "calendar_id": new_plan.id,
                            "date_start": "2024-05-01",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "calendar_id": old_plan.id,
                            "date_start": "2024-01-01",
                            "date_end": "2024-04-30",
                        },
                    ),
                ],
            }
        )
        self.calendar = self.employee.resource_calendar_id
        self.leave_type = self.env["hr.leave.type"].create(
            {
                "name": "Test vacation",
                "requires_allocation": "no",
                "leave_validation_type": "hr",
                "request_unit": "day",
            }
        )

    def _leave_on(self, day):
        """Create a one day leave and make the dates recompute.

        date_from and date_to carry a default of "now", so a plain create
        never runs their compute. Writing the request dates afterwards marks
        them dirty and is also what the form does.
        """
        leave = self.env["hr.leave"].create(
            {
                "name": "Testabwesenheit",
                "employee_id": self.employee.id,
                "holiday_status_id": self.leave_type.id,
                "request_date_from": OTHER_FRIDAY,
                "request_date_to": OTHER_FRIDAY,
            }
        )
        leave.write({"request_date_from": day, "request_date_to": day})
        return leave

    def test_dates_follow_the_currently_valid_attendance(self):
        """Expired lines must not decide when the leave starts or ends"""
        leave = self._leave_on(FRIDAY)
        self.assertEqual(
            fields.Datetime.to_string(leave.date_from),
            EXPECTED_FROM,
            "start taken from the expired 08:00 line",
        )
        self.assertEqual(
            fields.Datetime.to_string(leave.date_to),
            EXPECTED_TO,
            "end taken from the expired 15:00 afternoon line",
        )

    def test_full_day_counts_as_one(self):
        """The symptom: a day short of an hour is booked as a fraction"""
        self.assertEqual(self._leave_on(FRIDAY).number_of_days, 1.0)

    def test_times_sent_along_are_corrected_too(self):
        """The interface supplies the times itself, which skips the compute

        Clicking a day in the calendar puts date_from and date_to into the
        context as defaults, and the form sends them on save. A field that
        arrives with a value is not computed, so _compute_date_from_to never
        runs for anything created through the interface - measured on
        2026-10-28, the module was loaded and the compute called zero times.
        The correction therefore has to happen on the record as well.
        """
        leave = self.env["hr.leave"].create(
            {
                "name": "Aus dem Kalender",
                "employee_id": self.employee.id,
                "holiday_status_id": self.leave_type.id,
                "request_date_from": FRIDAY,
                "request_date_to": FRIDAY,
                # what the expired lines would produce: 08:00 to 15:00 local
                "date_from": "2026-06-05 06:00:00",
                "date_to": "2026-06-05 13:00:00",
            }
        )
        self.assertEqual(fields.Datetime.to_string(leave.date_from), EXPECTED_FROM)
        self.assertEqual(fields.Datetime.to_string(leave.date_to), EXPECTED_TO)
        self.assertEqual(leave.number_of_days, 1.0)

    def test_approved_leaves_are_left_alone(self):
        """Rewriting the dates of a validated leave would zero its days

        It blocks its own working time through resource.calendar.leaves, and
        number_of_days counts against what is left of the calendar. On
        2026-10-28 a repair script that did not account for this set 498
        leaves to zero days.
        """
        leave = self._leave_on(FRIDAY)
        leave.action_validate()
        before = (leave.date_from, leave.date_to, leave.number_of_days)

        leave._align_stored_dates()

        self.assertEqual((leave.date_from, leave.date_to, leave.number_of_days), before)
