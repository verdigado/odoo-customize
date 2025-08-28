import base64
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

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

    @api.model
    def create(self, vals):
        record = super().create(vals)
        self = self.sudo()  # allow public users to search and create records
        employee = self.env["hr.employee"].search(
            [
                ("name", "=", record.employee_name),
            ],
            limit=1,
        )
        if not employee:
            logger.warning(
                f"Cannot create leave from leave request {record.id}: "
                f"Could not find employee {record.employee_name}"
            )
            return record

        leave_type = record.leave_type_id
        if not leave_type:
            logger.warning(
                f"Cannot create leave from leave request {record.id}: No default leave_type"
            )
            return record

        date_from = datetime.combine(record.start_date, datetime.min.time())
        date_to = datetime.combine(record.end_date, datetime.max.time())
        leave = self.env["hr.leave"].create(
            {
                "name": f"Leave from request {record.id}",
                "employee_id": employee.id,
                "holiday_status_id": leave_type.id,
                "date_from": date_from,
                "date_to": date_to,
            }
        )
        record.leave_id = leave
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
