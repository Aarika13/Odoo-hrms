# Tech name: aspl_hr_employee Version: 15 CE

# Description:
--------------

15.0.0.0.0
----------
Added hr applicant and employee module. override create employee method and updated skills on employee level from
applicant.

15.0.0.0.1
----------
38628 : Employee module migration from Odoo 9 to Odoo 15

15.0.0.0.2
----------
Fixed error and changes in code for 38854 and 38856. Added V9 id field in Employee V15 for match the records in the Odoo
RPC script.

15.0.0.0.3
----------
Added changes of 38917 and 38908.

15.0.0.0.4
----------
Changed type of relation field from M2O to selection and removed Education and Previous Employment Pages.

15.0.0.0.5
----------
38934: Issues in Documents opening in Employee Odoo 15.

15.0.0.0.6
----------
38933: Issues in Filter and group by in Employee Odoo 15.

15.0.0.0.7
----------
38938 : Issues in Employee bank details update in Odoo 15

15.0.0.0.8
----------
AM:
38935 - Need to calculate Relative Experience and Actual Experience based on resume lines in Odoo 15. 38932 - Issue in
Employee > Employee Identity in Odoo 15

15.0.0.0.9
----------
Fixed issues of Relative Experience and Actual Experience.

15.0.0.0.10
-----------
38952 : Need to improve below points in Employee Odoo 15

1) Move Work Details from Private Information to Work Information Page.
2) PF Account View : Need to remove extra group.
3) Need to add fields as in Employee Tree view as per Odoo9
4) Need to modify view structure of Private Information page from Col 3 to Col 2, As per ERP standard.

15.0.0.0.11
-----------
38954: Employee Security Group Correction 38953: Issues in Employee > Short Fall calculation Depend upon hr_holiday
module, we will fix after hr_holiday_aspire module migration, Currently commented the short fall calculation code.

15.0.0.0.12
-----------
38952:
Removed below fields and groups from the Private information page:

- Work Permit (Group)
- Education Detail (Group)
- Home-Work Distance
- Identification No
- Passport No
- Place of Birth
- Country of Birth
- Bank Account Number

15.0.0.0.13
-----------
Commented code for run odoo rpc script correctly.

15.0.0.0.14
-----------
Resolved error of employee own record opening in Information also added groups in existing menu's of Employee.

Migrated method from Odoo 9 to 15 for handle own access of employee records.

15.0.0.0.15
-----------
Restricted user creation from Employee due to default groups allocation in Users.

15.0.0.0.16
-----------
Issues in Relative and Actual Experience Added default filter in Employee and Employee directory. Added Employee
document type as Education Added widget for download document from tree view Updated the employee left code and return
to confirm and probation from left state.
