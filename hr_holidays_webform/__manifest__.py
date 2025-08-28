# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

{
    "name": "HR Holidays Webform",
    "summary": "Web form for employees to submit leaves without log-in",
    "version": "15.0.1.0.0",
    "category": "HR",
    "author": "verdigado eG",
    "maintainers": [],
    "license": "AGPL-3",
    "depends": [
        "hr_holidays",
        "cms_form",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/leave_requests_report_mail_template.xml",
        "data/cron_send_monthly_report.xml",
        "views/report.xml",
        "views/report_hr_leave_request_template.xml",
        "views/hr_leave_request.xml",
        "views/hr_leave.xml",
        "views/hr_leave_request_wizard.xml",
        "views/res_config_settings.xml",
    ],
    "demo": [],
}
