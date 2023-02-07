# verdigado attendance


## Features

* Employees can see and edit their attendances.
* ~~Remove column "Employee" from own attendances view.~~ --> Removed again as did not work in all situations.
* Add "Working Times" configuration menu to employees -> configuration
* Disable default filter for own attendances in report "All Employes"


## Access Rights

In file `ir.model.access.csv` the following access rules are defined and

1. Allow users to delete own attendance records

```
access_hr_attendance_user_verdigado,hr.attendance.user.verdigado,hr_attendance.model_hr_attendance,hr_attendance.group_hr_attendance,1,1,1,1
```

2. Allow users to access own reports (attendance statistics)

```
access_hr_attendance_report_verdigado,hr.attendance.report.verdigado,hr_attendance.model_hr_attendance_report,hr_attendance.group_hr_attendance,1,0,0,0
```


3. The HR manager can create and edit working times.

```
access_resource_calendar_officer_verdigado,resource.calendar.system,resource.model_resource_calendar,hr.group_hr_manager,1,1,1,1
```

```
access_resource_calendar_attendance_officer_verdigado,resource.calendar.attendance.system,resource.model_resource_calendar_attendance,hr.group_hr_manager,1,1,1,1
```
