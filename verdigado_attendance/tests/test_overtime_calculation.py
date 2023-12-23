# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime, time, timedelta

import pytz

from odoo import fields
from odoo.tests.common import TransactionCase


class TestOvertimeCalculation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.employeeA = cls.env["hr.employee"].create(
            {
                "name": "employeeA",
                # 40h/w
                "resource_calendar_id": cls.env.ref(
                    "resource.resource_calendar_std"
                ).id,
                "address_id": cls.env["res.partner"]
                .create(
                    {
                        "name": "EmployeeA",
                        "country_id": cls.env.ref("base.de").id,
                        "state_id": cls.env.ref("base.state_de_by").id,
                    }
                )
                .id,
            }
        )
        cls.employeeAallocation = cls.env["hr.leave.allocation"].create(
            {
                "employee_id": cls.employeeA.id,
                "holiday_type": "employee",
                "holiday_status_id": cls.env.ref("hr_holidays.holiday_status_cl").id,
                "number_of_days": 30,
                "date_from": "2023-01-01",
                "date_to": "2023-12-31",
            }
        )
        cls.employeeAallocation.action_confirm()
        cls.employeeAallocation.action_validate()
        cls.env["hr.holidays.public.generator"].create(
            {
                "year": 2023,
                "country_id": cls.env.ref("base.de").id,
            }
        ).action_run()
        cls.employeeA.company_id.write(
            {
                # TODO: fix odoo's off-by-one error here in hr.attendance#_get_attendances_dates
                "overtime_start_date": datetime(2023, 4, 2),
                "hr_attendance_overtime": True,
            }
        )

    def test_calculation_employeeA(self):
        """Test that the calculation works as expected for standard cases"""
        employeeA = self.employeeA

        # regular work
        self.record_time(employeeA, "2023-04-03", "07:10:00", "16:25:00")
        self.assertOvertime(employeeA, "2023-04-03", 1.25 * 60, 8 * 60)

        self.record_time(employeeA, "2023-04-04", "07:14:00", "15:35:00")
        self.assertOvertime(employeeA, "2023-04-04", 21, 8 * 60)

        self.take_leave(employeeA, "2023-04-05", "2023-04-06")

        # leaves taken from above
        self.record_time(employeeA, "2023-04-05", "00:00:00", "00:00:00")
        self.assertOvertime(employeeA, "2023-04-05", 0, 0)

        self.record_time(employeeA, "2023-04-06", "00:00:00", "00:00:00")
        self.assertOvertime(employeeA, "2023-04-06", 0, 0)

        # easter public holidays
        self.record_time(employeeA, "2023-04-07", "00:00:00", "00:00:00")
        self.assertOvertime(employeeA, "2023-04-07", 0, 0)

        self.record_time(employeeA, "2023-04-10", "00:00:00", "00:00:00")
        self.assertOvertime(employeeA, "2023-04-10", 0, 0)

        # just no show on work
        self.record_time(employeeA, "2023-04-11", "00:00:00", "00:00:00")
        self.assertOvertime(employeeA, "2023-04-11", -8 * 60)

        self.record_time(employeeA, "2023-04-12", "00:00:00", "00:00:00")
        self.assertOvertime(employeeA, "2023-04-12", -8 * 60)

        self.record_time(employeeA, "2023-04-13", "00:00:00", "00:00:00")
        self.assertOvertime(employeeA, "2023-04-13", -8 * 60)

        self.record_time(employeeA, "2023-04-14", "00:00:00", "00:00:00")
        self.assertOvertime(employeeA, "2023-04-14", -8 * 60)

        # regular work
        self.record_time(employeeA, "2023-04-17", "06:31:00", "15:10:00")
        self.assertOvertime(employeeA, "2023-04-17", 39)

        self.record_time(employeeA, "2023-04-18", "06:58:00", "12:30:00")
        self.assertOvertime(employeeA, "2023-04-18", -(2 * 60 + 28))

        self.record_time(employeeA, "2023-04-19", "06:39:00", "14:45:00")
        self.assertOvertime(employeeA, "2023-04-19", 6)

        self.record_time(employeeA, "2023-04-20", "06:19:00", "14:27:00")
        self.assertOvertime(employeeA, "2023-04-20", 8)

        self.record_time(employeeA, "2023-04-21", "08:10:00", "15:18:00")
        self.assertOvertime(employeeA, "2023-04-21", -52)

        self.record_time(employeeA, "2023-04-24", "06:45:00", "15:22:00")
        self.assertOvertime(employeeA, "2023-04-24", 37)

        self.record_time(employeeA, "2023-04-25", "07:15:00", "17:20:00")
        self.assertOvertime(employeeA, "2023-04-25", 2 * 60 + 5)

        self.record_time(employeeA, "2023-04-26", "06:50:00", "14:30:00")
        self.assertOvertime(employeeA, "2023-04-26", -20)

        self.record_time(employeeA, "2023-04-27", "07:42:00", "17:00:00")
        self.assertOvertime(employeeA, "2023-04-27", 60 + 18)

        self.record_time(employeeA, "2023-04-28", "08:33:00", "12:45:00")
        self.assertOvertime(employeeA, "2023-04-28", -(3 * 60 + 48))

        self.record_time(employeeA, "2023-04-30", "09:30:00", "14:45:00")
        self.assertOvertime(employeeA, "2023-04-30", 5 * 60 + 15)

        # corpus christi, specific to some states
        attendance = self.record_time(employeeA, "2023-08-06", "09:00:00", "17:00:00")
        overtime = self.assertOvertime(employeeA, "2023-08-06", 8 * 60, 0)
        overtime.unlink()
        # and test that updating an attendance yields the same result
        attendance.check_out += timedelta(hours=1)
        self.assertOvertime(employeeA, "2023-08-06", 9 * 60, 0)

        # be sure that a day spanning attendance generates overtime records for all days
        attendance.check_out += timedelta(days=1)
        self.assertOvertime(employeeA, "2023-08-06", 33 * 60, 0)
        self.assertOvertime(employeeA, "2023-08-07", 0, 8 * 60)

    def to_time(self, time_string):
        if isinstance(time_string, str):
            return datetime.strptime(time_string, "%H:%M:%S").time()
        return time_string

    def local_date_to_utc_datetime(self, employee, date_string):
        date = fields.Date.to_date(date_string)
        return (
            pytz.timezone(employee.tz)
            .localize(datetime.combine(date, time.min))
            .astimezone(pytz.utc)
            .replace(tzinfo=None)
        )

    def record_time(self, employee, date, checkin_time, checkout_time):
        date = fields.Date.to_date(date)
        checkin_time = self.to_time(checkin_time)
        checkout_time = self.to_time(checkout_time)

        tz = pytz.timezone(employee.tz)
        return self.env["hr.attendance"].create(
            {
                "employee_id": employee.id,
                "check_in": tz.localize(datetime.combine(date, checkin_time))
                .astimezone(pytz.utc)
                .replace(tzinfo=None),
                "check_out": tz.localize(datetime.combine(date, checkout_time))
                .astimezone(pytz.utc)
                .replace(tzinfo=None),
            }
        )

    def take_leave(self, employee, date_from, date_to):
        leave = self.env["hr.leave"].create(
            {
                "employee_id": employee.id,
                "date_from": self.local_date_to_utc_datetime(employee, date_from),
                "date_to": self.local_date_to_utc_datetime(employee, date_to)
                + timedelta(days=1),
                "holiday_status_id": self.env.ref("hr_holidays.holiday_status_cl").id,
            }
        )
        leave.action_approve()
        leave.action_validate()

    def assertOvertime(self, employee, date, minutes, expected_minutes=None):
        overtime = self.env["hr.attendance.overtime"].search(
            [
                ("employee_id", "=", employee.id),
                ("date", "=", date),
                ("adjustment", "=", False),
            ]
        )
        self.assertEqual(
            round(sum(overtime.mapped("duration")), 2), round(minutes / 60, 2)
        )
        self.assertEqual(
            expected_minutes and round(sum(overtime.mapped("expected_hours")), 2),
            expected_minutes and round(expected_minutes / 60, 2),
        )
        return overtime
