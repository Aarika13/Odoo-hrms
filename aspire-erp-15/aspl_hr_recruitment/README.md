# Tech name: aspl_hr_recruitment Version: 14 CE

# Description:
--------------
Modified Default Recruitment Flow as per Aspire Software Solution Requirement.

Added Data files for Skills, tags, Stages, Degree, Hr Que, Refuse Reasons etc. Added Group for Recruitment User. Added
Record Rule for Interviewers Removed Responsible from Job Opening and Applications

Added Job Positions as per Odoo 9. Added Record rules for User, Officer and Manager Modified code refuse reason and
stages Added no create, edit in all the relational fields of Job Opening and Applications. Added Groups at menu level
for User Added Configuration models access to the new created User group.

skills updated on interviewer feedbacks. code optimization of skill average calculation.

skill feedback update while applicant goes to offer stage or refuse stage. Added source id field in candidates.

15.0.0.0.1
----------
Modified code for Skill value update in Application.

15.0.0.0.2
----------
Log recruitment activities

15.0.0.0.3
----------
Fixed Issues of Skill update from Application to candidate

15.0.0.0.4
----------
Recruitment Excel report

15.0.0.0.5
----------
38531 : Develop source of Hire report.

Used existing model to fetch the sources per Hire count in pivot report.

15.0.0.0.6
----------
38540 : Applicants per hire report

Created new model and PostgreSQL view for fetch the count in pivot report.

15.0.0.0.7
----------
Added Mail Template with Dynamic Data. Added Changes on Stage.

15.0.0.0.8
----------
38627 : Develop Time to hire report 38625 : Develop Vacancies vs. positions filled report

15.0.0.0.9
----------
38629 : Issues fixing related to Recruitment Odoo15

1) email: interest - shows error.
2) If we click on progress error is occur application - initial stage - candidate profile
3) Candidate > create - without entering any details it gets saved just by entering the candidate name
4) job opening > without entering any details it gets saved just by entering the job position name

15.0.0.0.10
-----------
38624 : Develop Offer acceptance per hire report.

15.0.0.0.11
-----------
Added Mail Template with Dynamic Data. Added Changes on Stage. Fixed Issue for buttons to be display as per stage.

15.0.0.0.12
-----------
Added changes of 38625 : Develop Vacancies vs. positions filled report, 38624 : Develop Offer acceptance per hire report
and 38626 : Develop Candidate experience report

15.0.0.0.13
-----------
38403 : Improvement Points of Odoo 15 Recruitments

Made below fields as mandatory in Job Opening:
Job Opening, Tags, Degree, Job Position, Priority, Department, Expected new employee, Recruiter

Made below fields as mandatory in Applications:
Subject / Application Name, Email, Reviewer, Interviewers, Recruiter, Tags, Degree, Applied Job, Mobile

Made below fields as mandatory in Candidate:
Name, Email, Mobile, Skills

15.0.0.0.14
-----------
38403 : Improvement Points of Odoo 15 Recruitments Replaced Job opening instead of applied job in All Applications
Modified code for 38626 : Candidate Experience Report.

15.0.0.0.15
-----------
38861: Job Opening Report Changes

38629: Issues fixing related to Recruitment Odoo15

15.0.0.0.16
-----------
39023: Issues in automatic Candidate creation by the incoming email server

15.0.0.0.17
-----------
39033: Needs to restrict Create in all views of Recruitment > Applications > All Applications.

15.0.0.0.18
-----------
Added manager level groups for Recruitment Configuration. Removed manager level group from Candidate chatter for check
the resume from chatter. Added groups for contact information. Passed private note from candidates to Application. Added
login user as default Recruiter in Job Opening.

15.0.0.0.19
-----------
Modified access rights for User, Officer and Manager. Removed tracking from expected current CTC from Candidate chatter.

15.0.0.0.20
-----------
Added date received from candidate to application creation.
Removed comma from Years of passing.
Renamed Current Location city to Current city.
Modified context for resolve issues of application creation.
Added department from Opening to application creation.

15.0.0.0.21
-----------
-Application create option from candidate by using wizard and in the selection option of respective Job openings
selection.
-In the Application View:
Remove Clickable from Applied Job, Degree, Source, Current Company, Current City, Department.

15.0.0.0.22
-----------
-Interviewer Screen (Pop-up) - When the interviewer adds his comments in that screen we need the following changes:
Change the Interview Date to Date Time Field 
Add Interview Time field - to denote how much time it took for the
interview (Required)
Add Status Field: Selected/Rejected/OnHold 
Add Comment Field: The interviewer will be able to add his comments here.

In Job Opening:	In the Kanban and List View: The default filter selected should be "Active"

15.0.0.0.23
-----------
In the Candidate View:
Remove clickable fields on Degree, Applied Job, Current City & Source.
On click of Current Company, it should show the list of candidates in that company.
