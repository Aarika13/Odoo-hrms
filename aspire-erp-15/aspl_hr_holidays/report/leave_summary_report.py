# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from math import ceil
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

import logging

_logger = logging.getLogger(__name__)


class LastMonthLeaveSummaryReport(models.AbstractModel):
    """docstring for last_month_leave_summary_report"""
    _name = 'report.hr_holidays_aspire.last_month_leave_summary_report_view'

    def _get_header_info(self, data):

        res = {}
        res['startDate'] = datetime.strptime(data['form']['startDate'], '%Y-%m-%d').strftime('%d-%b-%Y')
        res['endDate'] = datetime.strptime(data['form']['endDate'], '%Y-%m-%d').strftime('%d-%b-%Y')
        res['reportType'] = data['form']['reportType']
        return res

    def _get_company_info(self, cr, uid, ids, context):

        userObj = self.pool.get('res.users')
        userObjId = userObj.search(cr, uid, [('id', '=', uid)], context=context)
        userObjData = userObj.browse(cr, uid, userObjId, context=context)
        company = userObjData.company_id
        res = []
        for record in company:
            companyName = dict(name=record.name, street=record.street, street2=record.street2, city=record.city,
                               zip=record.zip)
            res.append(companyName)
        return res

    def check_user_permissions(self, cr, uid, ids, context):
        role = None
        groupbject = self.pool['res.groups']
        groupHrID = groupbject.search(cr, uid, [('name', '=', 'Officer')])
        groupHrData = groupbject.browse(cr, uid, groupHrID)
        groupReportingID = groupbject.search(cr, uid, [('name', '=', 'Reporting Authority')])
        groupReportingData = groupbject.browse(cr, uid, groupReportingID)
        if uid in groupHrData.users.ids:
            role = "HR"
        return role

    def check_user_attendance(self, cr, uid, ids, datefrom, dateto, employee_id, enddate, record, context):
        dataList = []
        diff = datetime.strptime(dateto, '%m-%d-%Y').date() - datetime.strptime(datefrom, '%m-%d-%Y').date()
        attenRecSumObj = self.pool.get('attendance.daily_summary')
        for i in range(diff.days + 1):
            dataDate = datetime.strptime(datefrom, '%m-%d-%Y').date() + timedelta(i)
            dataOfLeave = {}
            attenRecSumId = attenRecSumObj.search(cr, uid, [('emp_id', '=', employee_id), ('date', '=', dataDate)])
            attenRecSumData = attenRecSumObj.browse(cr, uid, attenRecSumId)
            if attenRecSumId and diff.days == 0:
                if record.from_session == record.to_session:
                    if record.from_session == 'session2' and datetime.strptime(attenRecSumData.out_time,
                                                                               '%H:%M:%S').time() >= datetime.strptime(
                        '16:00:00', '%H:%M:%S').time():
                        dataOfLeave['from'] = dataDate
                        dataOfLeave['to'] = dataDate
                        dataList.append(dataOfLeave)
                    elif record.from_session == 'session1' and datetime.strptime(attenRecSumData.in_time,
                                                                                 '%H:%M:%S').time() <= datetime.strptime(
                        '13:00:00', '%H:%M:%S').time():
                        dataOfLeave['from'] = dataDate
                        dataOfLeave['to'] = dataDate
                        dataList.append(dataOfLeave)
                else:
                    dataOfLeave['from'] = dataDate
                    dataOfLeave['to'] = dataDate
                    dataList.append(dataOfLeave)
            elif attenRecSumId and diff.days > 0:
                if record.from_session == record.to_session:
                    if record.from_session == 'session2' and datetime.strptime(attenRecSumData.out_time,
                                                                               '%H:%M:%S').time() >= datetime.strptime(
                        '16:00:00', '%H:%M:%S').time():
                        dataOfLeave['from'] = dataDate
                        dataOfLeave['to'] = dataDate
                        if dataDate == datetime.strptime(datefrom, '%m-%d-%Y').date():
                            dataOfLeave['halfDay'] = '0.5'
                            dataList.append(dataOfLeave)
                        else:
                            if len(dataList) > 0:
                                if dataList[-1]['to'] + timedelta(1) == dataOfLeave['from']:
                                    dataList[-1]['to'] = dataOfLeave['to']
                                else:
                                    dataList.append(dataOfLeave)
                            else:
                                dataList.append(dataOfLeave)

                    elif record.from_session == 'session1' and datetime.strptime(attenRecSumData.in_time,
                                                                                 '%H:%M:%S').time() <= datetime.strptime(
                        '13:00:00', '%H:%M:%S').time():
                        dataOfLeave['from'] = dataDate
                        dataOfLeave['to'] = dataDate
                        if dataDate == datetime.strptime(dateto, '%m-%d-%Y').date():
                            dataOfLeave['halfDay'] = '0.5'
                            dataList.append(dataOfLeave)
                        else:
                            if len(dataList) > 0:
                                if dataList[-1]['to'] + timedelta(1) == dataOfLeave['from']:
                                    dataList[-1]['to'] = dataOfLeave['to']
                                else:
                                    dataList.append(dataOfLeave)
                            else:
                                dataList.append(dataOfLeave)
                else:
                    if record.to_session == 'session1' and record.from_session == 'session2':
                        dataOfLeave['from'] = dataDate
                        dataOfLeave['to'] = dataDate
                        if dataDate == datetime.strptime(dateto, '%m-%d-%Y').date() and datetime.strptime(
                                attenRecSumData.in_time, '%H:%M:%S').time() <= datetime.strptime('13:00:00',
                                                                                                 '%H:%M:%S').time():
                            dataOfLeave['halfDay'] = '0.5'
                            dataList.append(dataOfLeave)
                        elif dataDate == datetime.strptime(datefrom, '%m-%d-%Y').date() and datetime.strptime(
                                attenRecSumData.in_time, '%H:%M:%S').time() >= datetime.strptime('16:00:00',
                                                                                                 '%H:%M:%S').time():
                            dataOfLeave['halfDay'] = '0.5'
                            dataList.append(dataOfLeave)
                        elif dataDate != datetime.strptime(dateto, '%m-%d-%Y').date() and dataDate != datetime.strptime(
                                datefrom, '%m-%d-%Y').date():
                            if len(dataList) > 0 and 'halfDay' not in dataList[-1]:
                                if dataList[-1]['to'] + timedelta(1) == dataOfLeave['from']:
                                    dataList[-1]['to'] = dataOfLeave['to']
                                else:
                                    dataList.append(dataOfLeave)
                            else:
                                dataList.append(dataOfLeave)
                    else:
                        dataOfLeave['from'] = dataDate
                        dataOfLeave['to'] = dataDate
                        if len(dataList) > 0:
                            if dataList[-1]['to'] + timedelta(1) == dataOfLeave['from']:
                                dataList[-1]['to'] = dataOfLeave['to']
                            else:
                                dataList.append(dataOfLeave)
                        else:
                            dataList.append(dataOfLeave)
        return dataList

    def get_employee_list(self, cr, uid, ids, context):
        employeeObject = self.pool['hr.employee']
        selfemployeeId = employeeObject.search(cr, uid, [('user_id', '=', uid)])
        selfemployeeData = employeeObject.browse(cr, uid, selfemployeeId)
        employeeId = employeeObject.search(cr, uid,
                                           [('with_organization', '=', True), ('parent_id', '=', selfemployeeData.id),
                                            ('employee_no_type', '!=', 'temporary_employee')])
        return employeeId

    def check_working_day(self, cr, uid, ids, dataDate, context):
        isWorking = False
        usersObj = self.pool['res.users']
        companyObj = self.pool['res.company']
        usersData = usersObj.browse(cr, uid, [uid], context)
        dateCode = 'W' + str(self.week_of_month(cr, uid, ids, dataDate, context)) + dataDate.strftime("%A")[:3]
        sql = 'SELECT "' + dateCode + '" FROM public.res_company where id = ' + str(usersData.company_id.id);
        cr.execute(sql)
        rows = cr.fetchall()
        for i in rows[0]:
            if i:
                isWorking = True
        return isWorking

    def getUnAppliedLeaves(self, cr, uid, ids, startdate, enddate, context):
        res = []
        employeeObject = self.pool['hr.employee']
        role = self.check_user_permissions(cr, uid, ids, context)
        if role == 'HR':
            employeeId = employeeObject.search(cr, uid, [('with_organization', '=', True),
                                                         ('employee_no_type', '!=', 'temporary_employee')])
        else:
            empIds = self.get_employee_list(cr, uid, ids, context)
            employeeId = employeeObject.search(cr, uid, [('with_organization', '=', True), ('id', 'in', empIds),
                                                         ('employee_no_type', '!=', 'temporary_employee')])
        employeeData = employeeObject.browse(cr, uid, employeeId)
        attenRecSumObj = self.pool.get('attendance.daily_summary')
        for employee in employeeData:
            diff = enddate.date() - startdate.date()
            for i in range(diff.days + 1):
                unAppliedData = {}
                dataDate = startdate.date() + timedelta(i)
                if not self.check_public_holidays(cr, uid, ids, dataDate, context):
                    if self.check_working_day(cr, uid, ids, dataDate, context):
                        unAppliedData['from'] = dataDate
                        unAppliedData['to'] = dataDate
                        unAppliedData['empName'] = employee.name
                        unAppliedData['empCode'] = employee.employee_no
                        unAppliedData['empManagerName'] = employee.parent_id.name
                        unAppliedData['empManagerCode'] = employee.parent_id.employee_no
                        if len(res) > 0:
                            if res[-1]['to'] + timedelta(1) == unAppliedData['from'] and res[-1]['empName'] == \
                                    unAppliedData['empName']:
                                res[-1]['to'] = unAppliedData['to']
                            else:
                                res.append(unAppliedData)
                        else:
                            res.append(unAppliedData)

                # if self.week_of_month(cr, uid, ids,dataDate,context) == 1 and dataDate.weekday() != 6 :
                # 	attenRecSumId = attenRecSumObj.search(cr,uid,[('emp_id','=',employee.id),('date','=',dataDate)])
                # 	if not attenRecSumId:
                # 		if not self.check_user_leaves(cr, uid, ids,dataDate,employee,context):
                # 			unAppliedData['from'] = dataDate
                # 			unAppliedData['to'] = dataDate
                # 			unAppliedData['empName'] = employee.name
                # 			unAppliedData['empCode'] = employee.employee_no
                # 			unAppliedData['empManagerName'] = employee.parent_id.name
                # 			unAppliedData['empManagerCode'] = employee.parent_id.employee_no
                # 			if len(res) > 0:
                # 				if res[-1]['to'] +  timedelta(1) == unAppliedData['from'] and res[-1]['empName'] == unAppliedData['empName']:
                # 					res[-1]['to'] = unAppliedData['to']
                # 				else:
                # 					res.append(unAppliedData)
                # 			else:
                # 				res.append(unAppliedData)
                # else:
                # 	if dataDate.weekday() != 5 and dataDate.weekday() != 6:
                # 		attenRecSumId = attenRecSumObj.search(cr,uid,[('emp_id','=',employee.id),('date','=',dataDate)])
                # 		if not attenRecSumId:
                # 			if not self.check_user_leaves(cr, uid, ids,dataDate,employee,context):
                # 				unAppliedData['from'] = dataDate
                # 				unAppliedData['to'] = dataDate
                # 				unAppliedData['empName'] = employee.name
                # 				unAppliedData['empCode'] = employee.employee_no
                # 				unAppliedData['empManagerName'] = employee.parent_id.name
                # 				unAppliedData['empManagerCode'] = employee.parent_id.employee_no
                # 				if len(res) > 0:
                # 					if res[-1]['to'] +  timedelta(1) == unAppliedData['from'] and res[-1]['empName'] == unAppliedData['empName']:
                # 						res[-1]['to'] = unAppliedData['to']
                # 					else:
                # 						res.append(unAppliedData)
                # 				else:
                # 					res.append(unAppliedData)

        return res

    def week_of_month(self, cr, uid, ids, dataDate, context):

        first_day = dataDate.replace(day=1)
        dom = dataDate.day
        adjusted_dom = dom + first_day.weekday()
        return int(ceil(adjusted_dom / 7.0))

    def check_user_leaves(self, cr, uid, ids, dataDate, employee, context):

        isLeave = False
        leaveobject = self.pool['hr.leave']
        leaveID = leaveobject.search(cr, uid, [('type', '=', 'remove'), ('employee_id', '=', employee.id)])
        leaveData = leaveobject.browse(cr, uid, leaveID)
        if leaveData:
            flag = True
            for leave in leaveData:
                if leave.number_of_days * -1 >= 1 and flag:
                    diff = datetime.strptime(leave.date_to, DEFAULT_SERVER_DATETIME_FORMAT).date() - datetime.strptime(
                        leave.date_from, DEFAULT_SERVER_DATETIME_FORMAT).date()
                    for i in range(diff.days + 1):
                        leaveDate = datetime.strptime(leave.date_from,
                                                      DEFAULT_SERVER_DATETIME_FORMAT).date() + timedelta(i)
                        if leaveDate == dataDate:
                            isLeave = True
                            flag = False
        return isLeave

    def check_public_holidays(self, cr, uid, ids, dataDate, context):
        ispublic = False
        holidaysDetails = self.pool['hr.holidays.detail']
        holidaysDetailId = holidaysDetails.search(cr, uid, [])
        holidaysDetailData = holidaysDetails.browse(cr, uid, holidaysDetailId)
        for holidays in holidaysDetailData:
            if datetime.strptime(holidays.holiday_from, '%Y-%m-%d').date() == dataDate:
                ispublic = True
        return ispublic

    def _get_data_from_report(self, cr, uid, ids, data, context=None):

        startdate = datetime.strptime(data['form']['startDate'], '%Y-%m-%d')
        enddate = datetime.strptime(data['form']['endDate'], '%Y-%m-%d')
        reportType = data['form']['reportType']
        leaveobject = self.pool['hr.leave']

        # role = self.check_user_permissions(cr, uid, ids,context)
        res = []

        if reportType == 'approved':
            leaveID = leaveobject.search(cr, uid, [('type', '=', 'remove'), ('state', '=', 'validate')])
        elif reportType == 'toapprove':
            leaveID = leaveobject.search(cr, uid, [('type', '=', 'remove'), ('state', '=', 'confirm')])
        elif reportType == 'needtoreject':
            leaveID = leaveobject.search(cr, uid, [('type', '=', 'remove'), ('state', '!=', 'refuse')])
        if reportType != 'unapplied':
            leave = leaveobject.browse(cr, uid, leaveID)
            count = 1
            for record in leave:
                applieddate = datetime.strptime(record.create_date, '%Y-%m-%d %H:%M:%S')
                writedate = datetime.strptime(record.write_date, '%Y-%m-%d %H:%M:%S')
                datetime_object = datetime.strptime(record.date_from, '%Y-%m-%d %H:%M:%S')

                if (datetime_object.date() >= startdate.date() and datetime_object.date() <= enddate.date()):
                    dateto = datetime.strptime(record.date_to, '%Y-%m-%d %H:%M:%S').date()
                    for items in record.employee_id:
                        employeeObject = self.pool['hr.employee']
                        employee = employeeObject.browse(cr, uid, items.ids)
                        leavestatusobj = self.pool['hr.holidays.status']
                        leavestatusID = leavestatusobj.search(cr, uid, [])
                        lstatus = leavestatusobj.browse(cr, uid, leavestatusID)
                        for rec in employee:
                            if rec.employee_no_type != 'temporary_employee':
                                managerinfo = rec.parent_id
                                for item in managerinfo:
                                    managerID = item.id
                                    managre = employeeObject.browse(cr, uid, managerID)
                                    for recods in lstatus:
                                        if recods.sequence == record.sequence:
                                            datefrom = datetime_object.strftime('%m-%d-%Y')
                                            dateto = dateto.strftime('%m-%d-%Y')
                                            employee_id = rec.id
                                            if reportType == 'toapprove' or reportType == 'approved':
                                                employeeInfo = dict(no=count, name=rec.name, empid=rec.employee_no,
                                                                    managerno=managre.employee_no,
                                                                    managrename=managre.name,
                                                                    reason=record.name, days=record.number_of_days * -1,
                                                                    datefrom=datetime_object.strftime('%m-%d-%Y'),
                                                                    dateto=dateto,
                                                                    applieddate=applieddate.strftime('%m-%d-%Y'),
                                                                    approveddate=writedate.strftime('%m-%d-%Y'),
                                                                    status=recods.name,
                                                                    approver=record.write_uid.name, state=record.state)
                                                res.append(employeeInfo)
                                                count = count + 1
                                            elif reportType == 'needtoreject':
                                                leaveData = self.check_user_attendance(cr, uid, ids, datefrom, dateto,
                                                                                       employee_id, enddate, record,
                                                                                       context)
                                                if leaveData:
                                                    for i in range(len(leaveData)):
                                                        if 'halfDay' in leaveData[i]:
                                                            days = leaveData[i]['halfDay']
                                                        else:
                                                            if record.number_of_days * -1 < (((
                                                                    leaveData[i]['to'] - leaveData[i][
                                                                'from']).days) + 1):
                                                                days = record.number_of_days * -1
                                                            else:
                                                                days = (((leaveData[i]['to'] - leaveData[i][
                                                                    'from']).days) + 1)

                                                        employeeInfo = dict(no=count, name=rec.name,
                                                                            empid=rec.employee_no,
                                                                            managerno=managre.employee_no,
                                                                            managrename=managre.name,
                                                                            reason=record.name, days=days,
                                                                            datefrom=leaveData[i]['from'],
                                                                            dateto=leaveData[i]['to'],
                                                                            applieddate=applieddate.strftime(
                                                                                '%m-%d-%Y'),
                                                                            approveddate=writedate.strftime('%m-%d-%Y'),
                                                                            status=recods.name,
                                                                            approver=record.write_uid.name,
                                                                            state=record.state
                                                                            )
                                                        res.append(employeeInfo)
                                                        count = count + 1
        else:
            data = self.getUnAppliedLeaves(cr, uid, ids, startdate, enddate, context)
            count = 1
            if data:
                for i in range(len(data)):
                    days = (((data[i]['to'] - data[i]['from']).days) + 1)
                    employeeInfo = dict(no=count, name=data[i]['empName'], empid=data[i]['empCode'],
                                        managerno=data[i]['empManagerCode'], managrename=data[i]['empManagerName'],
                                        reason="N/A", days=days,
                                        datefrom=data[i]['from'],
                                        dateto=data[i]['to'],
                                        applieddate="N/A",
                                        approveddate="N/A", status="N/A",
                                        approver="N/A", state="Un-Applied"
                                        )
                    res.append(employeeInfo)
                    count = count + 1
        return res

    def render_html(self, cr, uid, ids, data, context=None):

        report_obj = self.pool['report']
        holidays_report = report_obj._get_report_from_name(cr, uid,
                                                           'hr_holidays_aspire.last_month_leave_summary_report_view')
        selected_records = self.pool['hr.leave'].browse(cr, uid, ids, context=context)
        docargs = {
            'doc_ids': ids,
            'doc_model': holidays_report.model,
            'docs': self,
            'get_data_from_report': self._get_data_from_report(cr, uid, ids, data, context=context),
            'get_company_info': self._get_company_info(cr, uid, ids, context=context),
            'get_header_info': self._get_header_info(data)
        }

        return report_obj.render(cr, uid, ids, 'hr_holidays_aspire.last_month_leave_summary_report_view', docargs,
                                 context=context)
