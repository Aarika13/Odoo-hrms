# Tech name: aspl_hr_equipment Version: 15 CE

# Description:
--------------
Equipment module migration from Odoo 9 to 15.

# Change Requests

#01: 9.0.0.1
---
Error in quick create material request.

#02: 9.0.0.1
---
We need Ticket No auto generated in Material Request. Added Ticket number in Tree and Search view. Make invisible
default sequence field.

15.0.0.0.2
----------
Modified scripts for maintenance equipment, maintenance request and equipment history. Added menu for Manufacturing and
Tag. Commented code of create method for run script correctly.

15.0.0.0.3
----------
39022: Need to add search filters and groups in Equipment

15.0.0.0.4
----------
Added groups as per Odoo 9 in Odoo 15 for Equipment Menu

15.0.0.0.5
----------
Created new group for handle own record access in Equipment and Maintenance Request

15.0.0.0.6
----------
Created Record rules for Maintenance requests. 39196: Issue in Maintenance request creation and need to add new created
group in MR header buttons.

15.0.0.0.7
----------
Migrated code for Replacing and replace with in Equipment.

15.0.0.0.8
----------
Added Warranty start data field in Equipment view. Modified Equipment name as editable Added Equipment number in form
view for check correct sequence.

