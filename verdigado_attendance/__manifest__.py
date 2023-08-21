# Copyright 2022 verdigado eG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Verdigado HR Attendance",
    "version": "15.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr-attendance",
    "author": "verdigado eG",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_attendance",
        "hr_holidays_attendance",
        "l10n_de_holidays",
        "hr_holidays_public_overtime",
    ],
    "data": [
        "data/hr_leave_type.xml",
        "data/res.lang.csv",
        "security/ir.model.access.csv",
        "security/hr_attendance_rule_attendance_manager.xml",
        "views/hr_attendance_view.xml",
        "views/hr_leave_type.xml",
        "views/hr_menu_human_resources_configuration.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "verdigado_attendance/static/src/scss/backend.scss",
        ],
        "web.assets_qweb": [
            "verdigado_attendance/static/src/xml/hr_holidays.xml",
        ],
    },
}
