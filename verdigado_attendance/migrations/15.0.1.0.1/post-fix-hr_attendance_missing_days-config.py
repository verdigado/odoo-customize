from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version=None):
    """Force load hr_attendance_missing_days' configuration"""
    openupgrade.load_data(
        env.cr,
        "verdigado_attendance",
        "data/ir_cron.xml",
    )
    openupgrade.load_data(
        env.cr,
        "verdigado_attendance",
        "data/res_company.xml",
    )
    # and recreate possibly missing overtime
    env["hr.attendance"].search([])._update_overtime()
