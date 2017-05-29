from tkinter import filedialog, messagebox, Tk
import csv
from datetime import datetime, time
from ast import literal_eval

class TimesheetFormatter:

    def __init__(self):
        self.root = Tk()
        self.root.overrideredirect(1)
        self.root.withdraw()

    ###################################
    ##  Driver
    ###################################

    def format(self):

        timesheetFile = self.getTimesheetFile()
        if not self.validateTimeSheet(timesheetFile):
            return
        else:
            timesheetData = self.loadTimeSheetInfo(timesheetFile)

        employeeFile = self.getEmployeeFile()
        if not self.validateEmployeeInfo(employeeFile):
            return
        else:
            employeeData = self.loadEmployeeInfo(employeeFile)

        dayLog = self.createDayLog(timesheetData)

        self.writeFormattedOutput(dayLog, employeeData, timesheetFile[:-4]+"_output.csv")


    ###################################
    ##  Business Logic
    ###################################

    # splits two-day shifts into two separate timesheet entries in the original
    # timesheetData
    def separate(self, timesheetData):

        for employee in timesheetData:
            logs = timesheetData[employee]

            for i in range(len(logs)):
                log = logs[i]
                startDate = log[0]
                endDate = log[2]

                if startDate.day != endDate.day:
                    startTime = log[1]
                    endTime = log[3]

                    startDate = startDate.combine(startDate, startTime.time())
                    midNight = endDate
                    endDate = endDate.combine(endDate, endTime.time())

                    new1 = [startDate,
                            startTime,
                            startDate,
                            time(23,59),
                            round((midNight - startDate).total_seconds() / 3600, 2)]

                    new2 = [endDate,
                            time(0,0),
                            endDate,
                            endTime,
                            round((endDate - midNight).total_seconds() / 3600, 2)]

                    logs.pop(i)
                    logs.insert(i, new2)
                    logs.insert(i, new1)



    # returns a mapping of each employee's id to their hours worked for each day
    def createDayLog(self, timesheetData):

        dayData = {}

        for employee in timesheetData:
            logs = timesheetData[employee]
            dayLog = {}

            for log in logs:
                day = log[0].date()

                if day not in dayLog:
                    dayLog[day] = 0

                dayLog[day] += log[4]

            dayData[employee] = dayLog

        return dayData


    ###################################
    ##  Writing / Ouput
    ###################################


    def writeFormattedOutput(self, dayLog, employeeData, outputFile):
        with open(outputFile, 'w+', newline='') as f:
            writer = csv.writer(f)

            errors = []

            for employee in dayLog:
                if employee in employeeData:
                    for date in sorted(dayLog[employee]):
                        output = [employeeData[employee][0],
                                  date.strftime("%m/%d/%Y"),
                                  str(round(dayLog[employee][date],2)),
                                  employeeData[employee][1],
                                  employeeData[employee][2]]
                        writer.writerow(output)
                else:
                    errors.append(employee)


        if len(errors) == 0:
            messagebox.showinfo("Completed",
                                 "Done!")
        else:
            messagebox.showwarning("Completed",
                                "Partial Completion: The following employees have logged time " + \
                                "but are not in your employee information file." +
                                "\n\n" + str(errors))

    def printTimesheet(self, timesheetData):

        for employee in timesheetData:
            logs = timesheetData[employee]

            for i in range(len(logs)):
                log = logs[i]

                output = employee + " " + log[0].strftime("%m/%d/%Y") + " " + log[1].strftime("%I:%M %p") + \
                         " " + log[2].strftime("%m/%d/%Y") + " " + log[3].strftime("%I:%M %p") + " " + str(log[4])

                print(output)

    ###################################
    ##  Loading
    ###################################


    def loadEmployeeInfo(self, employeeFile):
        with open(employeeFile) as f:
            reader = csv.reader(f)
            employeeData = {}
            next(reader)
            for row in reader:
                employeeData[row[0]] = row[1:]

        return employeeData

    def loadTimeSheetInfo(self, timesheetFile):
        with open(timesheetFile) as f:
            reader = csv.reader(f)
            timesheetData = {}
            next(reader)
            for row in reader:
                
                if row[0] not in timesheetData:
                    timesheetData[row[0]] = []
            
                timesheetData[row[0]].append([datetime.strptime(row[1], "%m/%d/%Y"),
                                            datetime.strptime(row[2], "%I:%M %p"),
                                            datetime.strptime(row[3], "%m/%d/%Y"),
                                            datetime.strptime(row[4], "%I:%M %p"),
                                            float(row[5])])
        return timesheetData

    ###################################
    ##  VALIDATION
    ###################################

    def validateEmployeeInfo(self, employeeFile):
        with open(employeeFile) as f:
            reader = csv.reader(f)
            next(reader)
            for i, row in enumerate(reader):
                if not len(row) == 4 or not row[0].isdigit() or len(row[1]) != 6:
                    messagebox.showerror("Error: Employee Info",
                                         "Incorrect Employee Info on Line " + str(i + 2) + " of " + employeeFile +
                                         "\n\nMust follow format provided in employee_info_example.csv!")
                    return False
        return True

    def validateTimeSheet(self, timesheetFile):

        with open(timesheetFile) as f:
            reader = csv.reader(f)
            next(reader)
            for i, row in enumerate(reader):
                if not len(row) == 6 or not row[0].isdigit() or not (row[5].isdigit() or isinstance(literal_eval(row[5]), float)):
                    pass
                else:
                    try:
                        datetime.strptime(row[1], "%m/%d/%Y")
                        datetime.strptime(row[3], "%m/%d/%Y")
                        datetime.strptime(row[2], "%I:%M %p")
                        datetime.strptime(row[4], "%I:%M %p")
                        continue
                    except ValueError as err:
                        pass

                messagebox.showerror("Error: Timesheet Info",
                                     "Incorrect Timesheet Info on Line " + str(i + 2) + " of " + timesheetFile +
                                     "\n\nMust follow format provided in timesheet_info_example.csv!")
                return False
        return True


    ###################################
    ##  Getting the file paths
    ###################################

    def getTimesheetFile(self):
        messagebox.showinfo("Select Timesheet Information",
                            "In the next prompt, select your TIMESHEET INFORMATION.")
        while (True):
            timesheetFile= filedialog.askopenfilename()
            if timesheetFile:
                break
            messagebox.showerror("Error: Select File",
                                 "You must select the timesheet information!")

        return timesheetFile

    def getEmployeeFile(self):
        messagebox.showinfo("Select Employee Information",
                            "In the next prompt, select your EMPLOYEE INFORMATION.")

        while (True):
            employeeFile = filedialog.askopenfilename()
            if employeeFile:
                break
            messagebox.showerror("Error: Select File",
                                 "You must select the employee information!")

        return employeeFile


if __name__ == "__main__":
    TimesheetFormatter().format()