# Copyright 2023 Hunki Enterprises BV
# Copyright 2026 verdigado eG
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

# 2024-06-03 is a Monday, so this is exactly one working week. The timestamps
# are UTC and span whole days on purpose, the test calendar works 08:00-17:00
# Europe/Berlin.
WEEK_FROM = "2024-06-03 00:00:00"
WEEK_TO = "2024-06-07 23:59:59"
# Wednesday and Thursday of the same week
SICK_FROM = "2024-06-05 00:00:00"
SICK_TO = "2024-06-06 23:59:59"
# the Thursday, so it falls inside the overlap
PUBLIC_HOLIDAY = "2024-06-06"


class TestHrHolidaysOverlap(TransactionCase):
    """Everything is set up from scratch on purpose.

    The demo data of hr_holidays is dated relative to today, which makes it
    fail or shift depending on when the suite runs.
    """

    def setUp(self):
        super().setUp()
        self.calendar = self.env["resource.calendar"].create(
            {
                "name": "Overlap test calendar",
                "tz": "Europe/Berlin",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "%s %s" % (day, period),
                            "dayofweek": str(index),
                            "hour_from": hour_from,
                            "hour_to": hour_to,
                            "day_period": period,
                        },
                    )
                    for index, day in enumerate(
                        ["Mon", "Tue", "Wed", "Thu", "Fri"],
                    )
                    for period, hour_from, hour_to in (
                        ("morning", 8.0, 12.0),
                        ("afternoon", 13.0, 17.0),
                    )
                ],
            }
        )
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Overlap Tester",
                "resource_calendar_id": self.calendar.id,
            }
        )
        self.vacation_type = self.env["hr.leave.type"].create(
            {
                "name": "Test vacation",
                "requires_allocation": "yes",
                "allocation_validation_type": "no",
                "leave_validation_type": "hr",
                "request_unit": "day",
                "can_overlap": False,
                "exclude_public_holidays": True,
            }
        )
        self.sick_type = self.env["hr.leave.type"].create(
            {
                "name": "Test sickness",
                "requires_allocation": "no",
                "leave_validation_type": "hr",
                "request_unit": "day",
                "can_overlap": True,
            }
        )
        # without an end date, so the assertions do not depend on today
        self.allocation = self.env["hr.leave.allocation"].create(
            {
                "name": "Test allocation",
                "holiday_status_id": self.vacation_type.id,
                "employee_id": self.employee.id,
                "holiday_type": "employee",
                "allocation_type": "regular",
                "number_of_days": 20.0,
                "date_from": "2024-01-01",
                "date_to": False,
                "state": "validate",
            }
        )

    def _create_leave(self, leave_type, date_from, date_to):
        """Create and approve a leave, dates are UTC timestamps.

        Setting request_date_from and request_date_to is not enough: hr.leave
        only derives date_from and date_to from them through an onchange, so a
        plain create leaves both at their default of "now". The leave would
        then cover no working time at all, and action_validate rejects it as
        falling on a day the employee does not work.
        """
        leave = self.env["hr.leave"].create(
            {
                "name": "%s %s" % (leave_type.name, date_from),
                "employee_id": self.employee.id,
                "holiday_status_id": leave_type.id,
                "date_from": date_from,
                "date_to": date_to,
            }
        )
        leave.action_validate()
        return leave

    def _credits(self):
        return self.env["hr.leave.allocation"].search(
            [
                ("employee_id", "=", self.employee.id),
                ("overlap_sick_leave_id", "!=", False),
            ]
        )

    def _remaining(self):
        return self.vacation_type.get_employees_days([self.employee.id])[
            self.employee.id
        ][self.vacation_type.id]["virtual_remaining_leaves"]

    def test_credit_allocation_is_created(self):
        """An overlapped leave is credited back as a real allocation"""
        vacation = self._create_leave(self.vacation_type, WEEK_FROM, WEEK_TO)
        self.assertEqual(vacation.number_of_days, 5)
        self.assertFalse(self._credits())
        self.assertEqual(self._remaining(), 15)

        sick_leave = self._create_leave(self.sick_type, SICK_FROM, SICK_TO)

        credit = self._credits()
        self.assertEqual(len(credit), 1)
        self.assertEqual(credit.number_of_days, 2)
        self.assertEqual(credit.holiday_status_id, self.vacation_type)
        self.assertEqual(credit.overlap_sick_leave_id, sick_leave)
        self.assertEqual(credit.overlap_leave_id, vacation)
        # available from the day they were lost, and never expiring
        self.assertEqual(str(credit.date_from), "2024-06-03")
        self.assertFalse(credit.date_to)
        self.assertEqual(self._remaining(), 17)

    def test_credit_follows_the_sick_leave(self):
        """Withdrawing the sick leave takes the credit with it"""
        self._create_leave(self.vacation_type, WEEK_FROM, WEEK_TO)
        sick_leave = self._create_leave(self.sick_type, SICK_FROM, SICK_TO)
        self.assertEqual(len(self._credits()), 1)

        sick_leave.action_refuse()

        # refused, not deleted: hr_holidays forbids deleting an allocation that
        # is validated or already has leaves charged to it. Only validated
        # allocations count towards the balance, so refusing is enough.
        credit = self._credits()
        self.assertEqual(len(credit), 1)
        self.assertEqual(credit.state, "refuse")
        self.assertEqual(self._remaining(), 15)

    def test_sync_is_idempotent(self):
        """Running the sync again neither duplicates nor resizes the credit"""
        self._create_leave(self.vacation_type, WEEK_FROM, WEEK_TO)
        self._create_leave(self.sick_type, SICK_FROM, SICK_TO)
        self.assertEqual(len(self._credits()), 1)

        self.env["hr.leave"]._sync_overlap_credits_for_employees(self.employee)
        self.env["hr.leave"]._sync_overlap_credits_for_employees(self.employee)

        self.assertEqual(len(self._credits()), 1)
        self.assertEqual(self._credits().number_of_days, 2)

    def test_public_holiday_in_overlap_is_not_credited(self):
        """A day nobody works costs no leave, so there is nothing to give back.

        Regression test: the amount used to depend on the caller, because the
        public holiday handling is taken from the context. Being sick on a
        public holiday was credited in the dashboard but not on approval.
        """
        public_year = self.env["hr.holidays.public"].create({"year": 2024})
        self.env["hr.holidays.public.line"].create(
            {
                "name": "Test holiday",
                "date": PUBLIC_HOLIDAY,
                "year_id": public_year.id,
            }
        )
        self._create_leave(self.vacation_type, WEEK_FROM, WEEK_TO)
        self._create_leave(self.sick_type, SICK_FROM, SICK_TO)

        # the overlap spans two days, the second one is a public holiday
        self.assertEqual(self._credits().number_of_days, 1)

    def test_no_overlap(self):
        """Types not allowing overlap still refuse to overlap each other"""
        self._create_leave(self.vacation_type, WEEK_FROM, WEEK_TO)
        with self.assertRaisesRegex(
            ValidationError, "You can not set 2 time off that overlaps"
        ):
            self._create_leave(self.vacation_type, SICK_FROM, SICK_TO)
