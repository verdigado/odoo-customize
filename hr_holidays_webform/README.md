# HR Holidays Webform

## Description

Module for creating leaves via webform. The form is reachable under
/cms/create/hr.leave.request or by using the "Submit Leave Request" redirect buttons in
the check-in or log-in view. Data that is submitted via the form creates a
hr.leave.request record. Leave requests can be viewed in the Time Off - Leave Requests
view.

## Usage

To submit a leave request, fill the webform and click 'Submit'. Submitting a leave
request triggers multiple actions:

-   A hr.leave.request record is created.
-   A matching hr.leave record is created. The matching is done by searching hr.employee
    records by name. If no matching employee is found, no leave is created
    automatically. Leaves can be created manually from a leave request by using the
    Create Leave button.
-   A notification email is sent. The target address and content is determined by the
    'Leave Request Notification' mail template.

A monthly summary report is created automatically and sent to an email address based on
the 'Leave Request Monthly Report' email template.

## Configuration

-   It is required to define a default leave type for leave requests under Settings -
    Employees - Leave Requests. If no default leave type is configured, hr.leave records
    can not be created automatically. It is still possible to manually create hr.leave
    records from hr.leave.requests by using the wizard.
-   The notification email can be modified by editing the 'Leave Request Notification'
    mail template.
-   The summary report email can be modified by editing the 'Leave Request Monthly
    Report' mail template.
-   The report can be modified by editing the 'report_hr_leave_request_template' file.
-   The dates and frequency for the monthly report can be modified by editing the 'Leave
    Request Monthly Report' ir.cron record (scheduled action). However, the report will
    always contain all hr.leave.request records from the previous month.
