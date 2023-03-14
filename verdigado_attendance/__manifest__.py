# Copyright 2022 verdigado eG
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

{
    "name": "Verdigado HR Attendance Reason",
    "version": "15.0.1.0.0",
    "category": "Human Resources",
    "website": "https://git.verdigado.com/verdigado/odoo-customize/verdigado_attendance",
    "author": "verdigado eG",
    "license": "LGPL-3",
    "installable": True,
    "depends": ["hr_attendance", "hr_attendance_report_theoretical_time"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_attendance_view.xml",
        "views/hr_menu_human_resources_configuration.xml",
        "views/hr_attendance_theoretical_time_report.xml",
    ],
    "assets":
    {
        'web.assets_backend': [
            'verdigado_attendance/assets/messaging_menu.scss',
        ],
    }
}
