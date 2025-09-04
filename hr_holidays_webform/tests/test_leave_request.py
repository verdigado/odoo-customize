import datetime
import logging

from odoo import fields
from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class TestLeaveRequest(TransactionCase):
    def setUp(self):
        super().setUp()
        self.leave_type = self.env["hr.leave.type"].create(
            {
                "name": "Test Leave",
                "requires_allocation": "no",
            }
        )
        self.employee = self.env["hr.employee"].create(
            {
                "name": "John Doe",
            }
        )

    def test_webform_creates_leave_successfully(self):
        request = self.env["hr.leave.request"].create(
            {
                "employee_name": "John Doe",
                "start_date": "2023-01-02",
                "end_date": "2023-01-04",
                "leave_type_id": self.leave_type.id,
            }
        )

        leave = self.env["hr.leave"].search(
            [("name", "=", f"Leave from request {request.id}")]
        )
        self.assertTrue(leave, "Leave record was not created")
        self.assertEqual(leave.employee_id, self.employee, "Employee mismatch")
        self.assertEqual(
            leave.holiday_status_id, self.leave_type, "Leave type mismatch"
        )
        self.assertEqual(
            leave.request_date_from, datetime.date(2023, 1, 2), "Start date mismatch"
        )
        self.assertEqual(
            leave.request_date_to, datetime.date(2023, 1, 4), "End date mismatch"
        )
        self.assertEqual(
            leave.name, f"Leave from request {request.id}", "Name mismatch"
        )

    def test_webform_no_matching_employee(self):
        with self.assertLogs(level="WARNING") as cm:
            self.env["hr.leave.request"].create(
                {
                    "employee_name": "James Bond",
                    "start_date": fields.Date.today(),
                    "end_date": fields.Date.today(),
                    "leave_type_id": self.leave_type.id,
                }
            )

        leaves = self.env["hr.leave"].search([("employee_id", "=", self.employee.id)])
        self.assertFalse(
            leaves, "Leave record should not be created for unknown employee"
        )

        self.assertTrue(
            any("Could not find employee James Bond" in msg for msg in cm.output),
            f"Expected warning log not found. Got logs: {cm.output}",
        )

    def test_wizard_creates_leave(self):
        # name mismatch to trigger failure in auto-create
        request = self.env["hr.leave.request"].create(
            {
                "employee_name": "Johnny Doe",
                "start_date": "2023-01-02",
                "end_date": "2023-01-04",
                "leave_type_id": self.leave_type.id,
            }
        )
        leave = self.env["hr.leave"].search([("employee_id", "=", self.employee.id)])
        self.assertFalse(leave, "Unexpected leave record should not be created")

        wizard = self.env["hr.leave.request.wizard"].create(
            {
                "request_id": request.id,
                "employee_id": self.employee.id,
                "leave_type_id": self.leave_type.id,
                "start_date": "2023-01-02",
                "end_date": "2023-01-04",
            }
        )
        wizard.action_create_leave()

        leave = self.env["hr.leave"].search([("employee_id", "=", self.employee.id)])
        self.assertTrue(leave, "Wizard did not create leave record")
        self.assertEqual(
            leave.request_date_from, datetime.date(2023, 1, 2), "Start date mismatch"
        )
        self.assertEqual(
            leave.request_date_to, datetime.date(2023, 1, 4), "End date mismatch"
        )
        self.assertEqual(
            leave.name, f"Leave from request {request.id}", "Name mismatch"
        )

    def test_action_open_wizard_context(self):
        request = self.env["hr.leave.request"].create(
            {
                "employee_name": "John Doe",
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today(),
                "leave_type_id": self.leave_type.id,
            }
        )

        action = request.action_open_wizard()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "hr.leave.request.wizard")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["target"], "new")

        # Assert defaults are passed correctly
        context = action.get("context", {})
        self.assertEqual(context.get("default_request_id"), request.id)
        self.assertEqual(context.get("default_start_date"), request.start_date)
        self.assertEqual(context.get("default_end_date"), request.end_date)
        self.assertEqual(context.get("default_leave_type_id"), self.leave_type.id)
