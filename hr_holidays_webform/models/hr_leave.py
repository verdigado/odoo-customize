import base64
import logging

from dateutil.relativedelta import relativedelta

from odoo import fields, models

logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = "hr.leave"

    leave_request_id = fields.Many2one("hr.leave.request", string="Leave Request")

    def cron_generate_monthly_report(self):
        today = fields.Date.today()
        first_of_this_month = today.replace(day=1)
        first_of_last_month = first_of_this_month - relativedelta(months=1)
        last_of_last_month = first_of_this_month - relativedelta(days=1)
        default_leave_type = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("hr_leave_request.default_leave_type")
        )
        records = self.search(
            [
                ("date_from", ">=", first_of_last_month),
                ("date_to", "<=", last_of_last_month),
                (
                    "holiday_status_id",
                    "=",
                    int(default_leave_type) if default_leave_type else False,
                ),
                ("number_of_days", ">", 0),
            ]
        )

        if not records:
            return

        pdf_content, _ = self.env.ref(
            "hr_holidays_webform.report_hr_leave_pdf"
        )._render_qweb_pdf(records.ids)

        attachment = self.env["ir.attachment"].create(
            {
                "name": "Monthly_Leave_Report.pdf",
                "type": "binary",
                "datas": base64.b64encode(pdf_content),
                "res_model": "hr.leave",
                "res_id": records[0].id,
                "mimetype": "application/pdf",
            }
        )
        template = self.env.ref(
            "hr_holidays_webform.mail_template_hr_leave_monthly_report"
        )
        if template:
            # force_attachment prevents Odoo from regenerating attachments
            # defined in the template
            template.send_mail(
                records[0].id,
                force_send=True,
                email_values={"attachment_ids": [(6, 0, [attachment.id])]},
            )
