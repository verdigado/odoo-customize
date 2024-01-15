from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    group_ids = []
    for xmlid in (
        "base.group_allow_export",
        "base.group_private_addresses",
        "base.group_user",
        "base.group_partner_manager",
        "base.group_no_one",
        "mail.group_mail_template_editor",
        "hr_attendance.group_hr_attendance",
        "hr_holidays.group_hr_holidays_responsible",
        "verdigado_attendance.group_verdigado_employee",
    ):
        group_ids += env.ref(xmlid).ids

    env.ref("base.default_user").write(
        {
            "groups_id": [(6, 0, group_ids)],
        }
    )
