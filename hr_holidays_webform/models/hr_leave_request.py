import base64
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models

logger = logging.getLogger(__name__)


class HrLeaveRequest(models.Model):
    _name = "hr.leave.request"

    name = fields.Char(
        string="Request Name",
        compute="_compute_name",
        store=True,
    )
    employee_name = fields.Char(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    certificate_type = fields.Selection(
        selection=[
            ("none", "No Certificate"),
            ("cert", "Certificate"),
            ("e-cert", "E-Certificate"),
            ("child", "Child Sick Leave"),
        ],
        default="cert",
        required=True,
    )
    certificate_file = fields.Binary()
    leave_id = fields.Many2one("hr.leave")
    leave_type_id = fields.Many2one(
        "hr.leave.type",
        default=lambda self: int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("hr_leave_request.default_leave_type", 0)
        )
        or False,
    )

    @api.depends("employee_name", "start_date", "end_date")
    def _compute_name(self):
        for record in self:
            parts = []
            if record.employee_name:
                parts.append(record.employee_name)
            if record.start_date and record.end_date:
                parts.append(f"from {record.start_date} to {record.end_date}")
            record.name = (
                "Leave Request: " + " ".join(parts) if parts else "Leave Request"
            )

    def action_open_wizard(self):
        self.ensure_one()
        return {
            "name": "Create HR Leaves",
            "type": "ir.actions.act_window",
            "res_model": "hr.leave.request.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_request_id": self.id,
                "default_start_date": self.start_date,
                "default_end_date": self.end_date,
                "default_leave_type_id": self.leave_type_id.id,
            },
        }

    def create_leave_from_leave_request(
        self, employee_id, date_from=None, date_to=None, leave_type_id=None
    ):
        self.ensure_one()
        leave_type_id = leave_type_id or self.leave_type_id
        if not leave_type_id:
            logger.warning(
                f"Cannot create leave from leave request {self.id}: No leave_type"
            )
            return self.env["hr.leave"]

        if date_from is None:
            date_from = datetime.combine(self.start_date, datetime.min.time())
        if date_to is None:
            date_to = datetime.combine(self.end_date, datetime.max.time())
        vals = {
            "private_name": f"Leave from request {self.id}",
            "employee_id": employee_id,
            "holiday_status_id": leave_type_id.id,
            "date_from": date_from,
            "date_to": date_to,
            "leave_request_id": self.id,
        }
        vals.update(
            self.env["hr.leave"]
            .with_user(self.env.ref("base.public_user"))
            ._default_get_request_parameters(vals)
        )  # always use the public user, because logged-in users time zone shifts the date
        leave = self.env["hr.leave"].create(vals)
        if self.certificate_file:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": _("Leave Certificate"),
                    "type": "binary",
                    "datas": self.certificate_file,
                    "res_model": "hr.leave",
                    "res_id": leave.id,
                    "mimetype": "application/pdf",
                }
            )
            leave.write({"supported_attachment_ids": [(4, attachment.id)]})
        leave._compute_date_from_to()
        self.leave_id = leave
        return leave

    @api.model
    def create(self, vals):
        record = super().create(vals)
        template = self.env.ref("hr_holidays_webform.mail_template_hr_leave_request")
        if template:
            template.sudo().send_mail(record.id, force_send=True, raise_exception=False)
        employee = (
            self.env["hr.employee"]
            .sudo()
            .search(
                [
                    ("name", "=", record.employee_name),
                ],
                limit=1,
            )
        )
        if not employee:
            logger.warning(
                f"Cannot create leave from leave request {record.id}: "
                f"Could not find employee {record.employee_name}"
            )
            return record
        record.sudo().create_leave_from_leave_request(employee_id=employee.id)
        return record

    def cron_generate_monthly_report(self):
        today = fields.Date.today()
        first_of_this_month = today.replace(day=1)
        first_of_last_month = first_of_this_month - relativedelta(months=1)
        last_of_last_month = first_of_this_month - relativedelta(days=1)
        records = self.search(
            [
                ("create_date", ">=", first_of_last_month),
                ("create_date", "<=", last_of_last_month),
            ]
        )

        if not records:
            return

        pdf_content, _ = self.env.ref(
            "hr_holidays_webform.report_hr_leave_request_pdf"
        )._render_qweb_pdf(records.ids)

        attachment = self.env["ir.attachment"].create(
            {
                "name": "Monthly_Leave_Request_Report.pdf",
                "type": "binary",
                "datas": base64.b64encode(pdf_content),
                "res_model": "hr.leave.request",
                "res_id": records[0].id,
                "mimetype": "application/pdf",
            }
        )
        template = self.env.ref(
            "hr_holidays_webform.mail_template_hr_leave_request_monthly_report"
        )
        if template:
            # force_attachment prevents Odoo from regenerating attachments
            # defined in the template
            template.send_mail(
                records[0].id,
                force_send=True,
                email_values={"attachment_ids": [(6, 0, [attachment.id])]},
            )
