# Copyright 2022 verdigado eG
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Verdigado HR Attendance",
    "version": "15.0.1.0.1",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr-attendance",
    "author": "verdigado eG",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_attendance",
        "hr_attendance_autoclose",
        "hr_attendance_break",
        "hr_attendance_break_autoclose",
        "hr_holidays_attendance",
        "l10n_de_holidays",
        "hr_holidays_public_overtime",
    ],
    "data": [
        "data/hr_leave_type.xml",
        "data/res.lang.csv",
        "security/verdigado_attendance.xml",
        "security/ir.model.access.csv",
        "views/hr_attendance_view.xml",
        "views/hr_attendance_report.xml",
        "views/hr_leave_type.xml",
        "views/hr_menu_human_resources_configuration.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/res_users.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            "verdigado_attendance/static/src/scss/primary_variables.scss",
        ],
        "web.assets_frontend": [
            "verdigado_attendance/static/src/scss/frontend.scss",
        ],
        "web.assets_backend": [
            "verdigado_attendance/static/src/scss/backend.scss",
            "verdigado_attendance/static/src/js/systray.esm.js",
        ],
        "web.assets_qweb": [
            "verdigado_attendance/static/src/xml/hr_holidays.xml",
            "verdigado_attendance/static/src/xml/systray.xml",
        ],
    },
}
