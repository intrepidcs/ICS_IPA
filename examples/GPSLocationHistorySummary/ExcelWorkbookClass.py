import datetime
import xlsxwriter
import os
from ICS_IPA import IPAInterfaceLibrary

class ExcelWorkbook:
    def __init__(self, WorkbookName='WorkbookOutput'):
        ReportGenTimeStamp = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
        self.workbook = xlsxwriter.Workbook(WorkbookName)

    #  Insert a worksheet
    def add_worksheet(self, WorksheetName='Sheet1'):
        #  Create a worksheet, insert our data
        self.worksheet = self.workbook.add_worksheet(WorksheetName)
        #bold = self.workbook.add_format({'bold': True})
        #right_align = self.workbook.add_format({'align': 'right'})

    def write_row_to_worksheet(self, rownum, colnum, rowdata):
        #write_row(row, col, data[, cell_format]) row and col are base 0 index
        self.worksheet.write_row(rownum, colnum, rowdata)

    def AddFileInfoListSheet(self, dbFilePaths, RunningOnWivi):
        #  Add a worksheet with the file list.
        self.worksheet = self.workbook.add_worksheet("FileInputDetails")
        startDatesFormatted = []
        if RunningOnWivi:
            #write fileIDs column
            ids = [str(item['id']) for item in dbFilePaths]
            self.worksheet.write_string('A1', 'FileNumber')
            self.worksheet.write_string('B1', 'FileID')
            self.worksheet.write_column('B2', ids)
            col_width = max(map(len, ids)) + 2
            self.worksheet.set_column('B:B', col_width)
            #write startDate column
            #raw date is expressed in msec since 1/1/1970 need to convert to date
            startDates = [item['startDate'] for item in dbFilePaths]
            FileNumber = 0
            for item in startDates:
                FileNumber = FileNumber + 1
                self.worksheet.write_number(FileNumber, 0, FileNumber)
                startDateFormatted = datetime.datetime.fromtimestamp(float(item)/1000.)
                startDateFormatted = startDateFormatted.strftime("%Y-%m-%d %H:%M:%S")
                startDatesFormatted.append(startDateFormatted) 
            self.worksheet.write_string('C1', 'StartDate')
            self.worksheet.write_column('C2', startDatesFormatted)
            col_width = max(map(len, startDatesFormatted)) + 2
            self.worksheet.set_column('C:C', col_width)
            #write vehicle column
            vehicles = [str(item['vehicle']) for item in dbFilePaths]
            self.worksheet.write_string('D1', 'Vehicle')
            self.worksheet.write_column('D2', vehicles)
            col_width = max(map(len, vehicles)) + 2
            self.worksheet.set_column('D:D', col_width)
            #write filenames column
            filenameswithoutpath = [os.path.basename(item['path']) for item in dbFilePaths]
            self.worksheet.write_string('E1', 'FileName')
            self.worksheet.write_column('E2', filenameswithoutpath)
            col_width = max(map(len, filenameswithoutpath)) + 2
            self.worksheet.set_column('E:E', col_width)
        else:
            # In PC mode the filename and path are all that matter for each file
            file_names = [item['path'] for item in dbFilePaths]
            rownumber = 0
            for item in dbFilePaths:
                rownumber = rownumber + 1
                self.worksheet.write_string(0, 0, 'FileNumber')
                self.worksheet.write_string(0, 1, 'FileNameAndPath')
                self.worksheet.write_number(rownumber, 0, rownumber)
                self.worksheet.write_string(rownumber, 1, file_names[rownumber-1])
                col_width = max(map(len, file_names)) + 2
                self.worksheet.set_column('B:B', col_width)

    def CloseWorkbook(self):
        self.workbook.close()