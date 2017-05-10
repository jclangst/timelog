import csv
import datetime
from tkinter import filedialog

filename = filedialog.askopenfilename()
reader = csv.reader(open(filename))
writer = csv.writer(open(filename[:-4] + "_separated.csv", "w+"))

for row in reader:
    startDate = datetime.datetime.strptime(row[3], "%m/%d/%Y")
    endDate = datetime.datetime.strptime(row[4], "%m/%d/%Y")

    #if clock-in surpasses a single day
    if startDate.day != endDate.day:
        startDate = startDate.combine(startDate,
                                      datetime.datetime.strptime(row[10], "%I:%M %p").time())
        midNight = endDate

        endDate = endDate.combine(endDate,
                                  datetime.datetime.strptime(row[11], "%I:%M %p").time())

        #create entry for first date
        row[4] = row[3]
        row[6] = round((midNight - startDate).total_seconds() / 3600, 2)
        row[7] = row[6]
        row[11] = "11:59 PM"
        writer.writerow(row)

        #create entry for second date
        row[4] = startDate.strftime("%m/%d/%Y")
        row[3] = row[4]
        row[6] = round((endDate - midNight).total_seconds() / 3600,2)
        row[7] = row[6]
        row[10] = "12:00 AM"
        row[11] = endDate.strftime("%I:%M %p")
        writer.writerow(row)

    else:
        writer.writerow(row)