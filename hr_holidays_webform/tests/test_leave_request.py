import datetime
import logging
import re
from unittest.mock import patch

from odoo import fields
from odoo.tests.common import HttpCase, TransactionCase, tagged

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

    def test_create_leave_without_leave_type(self):
        leave_request = self.env["hr.leave.request"].create(
            {
                "name": "No Type Leave Request",
                "employee_name": "John Doe",
                "start_date": "2023-01-02",
                "end_date": "2023-01-04",
            }
        )

        leave = leave_request.create_leave_from_leave_request(self.employee.id)

        self.assertEqual(leave._name, "hr.leave")
        self.assertFalse(leave, "Leave sollte nicht erstellt werden ohne leave_type_id")

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

    def test_mail_sent_on_create(self):
        with patch("odoo.addons.mail.models.mail_mail.MailMail.create") as mock_create:
            self.env["hr.leave.request"].create(
                {
                    "employee_name": "John Doe",
                    "start_date": fields.Date.today(),
                    "end_date": fields.Date.today(),
                    "leave_type_id": self.leave_type.id,
                }
            )

            self.assertTrue(mock_create.called, "Mail was not triggered")


@tagged("post_install", "-at_install")  # run after modules are installed
class TestPublicLeaveRequestForm(HttpCase):
    def setUp(self):
        super().setUp()
        self.leave_type = self.env["hr.leave.type"].create(
            {
                "name": "Test Leave",
                "requires_allocation": "no",
            }
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "hr_leave_request.default_leave_type", self.leave_type.id
        )

    def test_public_user_can_submit_leave_request(self):
        # simulate a public HTTP POST request to form controller
        url = "/cms/create/hr.leave.request"
        form_html = self.url_open(url)
        token_match = re.search(
            r'name="csrf_token" value="(.+?)"', form_html.content.decode()
        )
        self.assertTrue(token_match, "CSRF token not found in form HTML")
        csrf_token = token_match.group(1)
        data = {
            "csrf_token": csrf_token,
            "certificate_type": "none",
            "employee_name": "Public User Employee",
            "start_date": "2025-09-15",
            "end_date": "2025-09-20",
        }

        response = self.url_open(url, data=data, timeout=30)

        self.assertEqual(response.status_code, 200)

        leave = self.env["hr.leave.request"].search(
            [("employee_name", "=", "Public User Employee")], limit=1
        )
        self.assertTrue(leave, "Public user submission did not create a record")
        self.assertEqual(leave.leave_type_id, self.leave_type)
