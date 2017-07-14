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


        self.separate(timesheetData)

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
            writer.writerow(["Employee ID", "State Number", "Job Code", "Pay Code", "Date", "Hours Logged"])

            errors = []

            for employee in dayLog:
                if employee in employeeData:
                    for date in sorted(dayLog[employee]):
                        output = [employee,
                                  employeeData[employee][0],
                                  employeeData[employee][1],
                                  employeeData[employee][2],
                                  date.strftime("%m/%d/%Y"),
                                  str(round(dayLog[employee][date],2))]

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
            labels = next(reader)

            for label in labels:
                for char in label:
                    if char.isdigit():
                        messagebox.showerror("Error: Timesheet Info",
                                             "It does not appear that the employee ID file has proper labels!\n\n"
                                             "The first row of the csv file should have the following labels on line 1:\n\n"
                                             "Employee ID,State Number,Job Code,Pay Code")

                        return False

            for i, row in enumerate(reader):
                if not len(row) == 4 or not row[0].isdigit() or len(row[1]) != 6:
                    messagebox.showerror("Error: Employee Info",
                                         "Incorrect Employee Info on Line " + str(i + 2) + " of " + employeeFile)
                    return False
        return True

    def validateTimeSheet(self, timesheetFile):
        error = 0

        with open(timesheetFile) as f:
            reader = csv.reader(f)
            labels = next(reader)

            for label in labels:
                for char in label:
                    if char.isdigit():
                        messagebox.showerror("Error: Timesheet Info",
                                             "It does not appear that the timesheet has proper labels!\n\n"
                                             "The first row of the csv file should have the following labels on line 1:\n\n"
                                             "Employee Id,Clock-In Date,Clock-In Time,Clock-Out Date, Clock-In Time,Hours Worked")

                        return False

            for i, row in enumerate(reader):
                if not len(row) == 6 or not row[0].isdigit() or not (row[5].isdigit() or isinstance(literal_eval(row[5]), float)):
                    pass
                else:
                    try:
                        error = 2
                        datetime.strptime(row[1], "%m/%d/%Y")
                        error = 4
                        datetime.strptime(row[3], "%m/%d/%Y")
                        error = 3
                        datetime.strptime(row[2], "%I:%M %p")
                        error = 5
                        datetime.strptime(row[4], "%I:%M %p")
                    except ValueError as err:

                        if(error == 2 or error == 4):
                            format = "mm/dd/yyyy"
                        else:
                            format = "hh:mm pm"

                        messagebox.showerror("Error: Timesheet Info",
                                             "Incorrect Timesheet Info on Line " + str(i + 2) + " Column " + str(error) +
                                             " of " + timesheetFile +".\n\n Correct format should be " + format + ".")
                        return False
        return True


    ###################################
    ##  Getting the file paths
    ###################################

    def getTimesheetFile(self):
        messagebox.showinfo("Select Timesheet Information",
                            "In the next prompt, select your TIMESHEET INFORMATION.")
        timesheetFile= filedialog.askopenfilename()
        if not timesheetFile:
            exit()

        return timesheetFile

    def getEmployeeFile(self):
        messagebox.showinfo("Select Employee Information",
                            "In the next prompt, select your EMPLOYEE INFORMATION.")


        employeeFile = filedialog.askopenfilename()
        if not employeeFile:
            exit()

        return employeeFile


if __name__ == "__main__":
    TimesheetFormatter().format()