# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import date, datetime, timedelta

from odoo.tests.common import TransactionCase


class TestOvertimeCalculation(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calendar = cls.env["resource.calendar"].create(
            {
                "name": "workdays morning",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "mon morning",
                            "dayofweek": "0",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "tue morning",
                            "dayofweek": "1",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "wed morning",
                            "dayofweek": "2",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "thu morning",
                            "dayofweek": "3",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "fri morning",
                            "dayofweek": "4",
                            "hour_from": 8,
                            "hour_to": 12,
                            "day_period": "morning",
                        },
                    ),
                ],
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "testemployee",
                "resource_calendar_id": cls.calendar.id,
            }
        )
        overtime_start = date.today() - timedelta(days=8)
        cls.employee.company_id.overtime_start_date = overtime_start
        cls.employee.theoretical_hours_start_date = overtime_start
        cls.env.cr.flush()
        cls.env["hr.attendance"]._overtime_from_theoretical_time()

    def _get_theoretical_time(self, employee):
        return self.env["hr.attendance.theoretical.time.report"].read_group(
            [("employee_id", "=", employee.id), ("date", "<", date.today())],
            ["theoretical_hours:sum", "worked_hours:sum", "difference:sum"],
            ["employee_id"],
        )[0]

    def test_calculation_standard(self):
        """Test that the calculation works as expected for standard cases"""
        theoretical_hours = self._get_theoretical_time(self.employee)
        self.assertEqual(
            theoretical_hours["difference"],
            -20,
            "Worked 0h last week while it should be 20",
        )
        self.assertEqual(
            self.employee.total_overtime,
            -20,
            "Worked 0h last week while it should be 20",
        )

        start_date = datetime.combine(
            self.employee.company_id.overtime_start_date, datetime.min.time()
        )
        self.env["hr.attendance"].create(
            {
                "employee_id": self.employee.id,
                "check_in": start_date + timedelta(days=1, hours=8),
                "check_out": start_date + timedelta(days=1, hours=12),
            }
        )
        self.env.cr.flush()
        theoretical_hours = self._get_theoretical_time(self.employee)
        self.assertEqual(
            theoretical_hours["difference"],
            -16,
            "Worked 4h last week while it should be 20",
        )
        self.assertEqual(
            self.employee.total_overtime,
            -16,
            "Worked 4h last week while it should be 20",
        )
        self.env["hr.attendance"].create(
            {
                "employee_id": self.employee.id,
                "check_in": start_date + timedelta(days=1, hours=13),
                "check_out": start_date + timedelta(days=1, hours=17),
            }
        )
        self.env.cr.flush()
        theoretical_hours = self._get_theoretical_time(self.employee)
        self.assertEqual(
            theoretical_hours["difference"],
            -12,
            "Worked 8h last week while it should be 20",
        )
        self.assertEqual(
            self.employee.total_overtime,
            -12,
            "Worked 8h last week while it should be 20",
        )
