import datetime
import xlsxwriter
import os
from ICS_IPA import IPAInterfaceLibrary

class ExcelHistogramReport:
    def __init__(self):
        ReportGenTimeStamp = datetime.datetime.now().strftime("%m-%d-%y_%H-%M-%S")
        OutputWorkbookName = "HistogramGen_" + ReportGenTimeStamp + ".xlsx" 
        self.workbook = xlsxwriter.Workbook(OutputWorkbookName)

    #  Given a Channel entry "sig_info" from the .asl file, insert a worksheet
    #  and populate it with the signal data and a histogram.
    def add_sig_worksheet(self, sig_info, hist):
        sig_name = sig_info["OptionalList"][0]["channel_name"]
        sig_script_name = sig_info["name_in_script"]
        bins = sig_info['bins']

        #  Create a workbook + worksheet, insert our data
        #  and a histogram (column chart)
        sheet_name = sig_name
        self.worksheet = self.workbook.add_worksheet(sheet_name)
        bold = self.workbook.add_format({'bold': True})
        right_align = self.workbook.add_format({'align': 'right'})

        #  Convert hist from an ndarray to an ordinary list
        #  and insert it into a worksheet column.
        bins.append("> " + str(bins[-1]))
        self.worksheet.write_column('A2', bins, right_align)
        self.worksheet.write_column('B2', hist)

        #  Insert a bar (column) chart created from the
        #  data inserted above.
        chart = self.workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': sig_name,
            'categories': [sheet_name, 1, 0, len(hist), 0],
            'values': [sheet_name, 1, 1, len(hist), 1],  # sheet, row, col, row, col
            'gap': 150
        })

        chart.set_x_axis({
            'position_axis': 'between'
        })

        chart.set_title({'name': sig_name})
        chart.set_legend({'none': True})

        #  Choose a chart style 1-48, as defined by Excel 2007
        chart.set_style(37)
        self.worksheet.insert_chart('D2', chart)

    def AddFileInfoListSheet(self, dbFilePaths, RunningOnWivi):
        #  Add a worksheet with the file list.
        self.worksheet = self.workbook.add_worksheet("FileInputDetails")
        startDatesFormatted = []
        if RunningOnWivi:
            #write fileIDs column
            ids = [str(item['id']) for item in dbFilePaths]
            self.worksheet.write_string('A1', 'FileID')
            self.worksheet.write_column('A2', ids)
            col_width = max(map(len, ids)) + 2
            self.worksheet.set_column('A:A', col_width)
            #write startDate column
            #raw date is expressed in msec since 1/1/1970 need to convert to date
            startDates = [item['startDate'] for item in dbFilePaths]
            for item in startDates:
                startDateFormatted = datetime.datetime.fromtimestamp(float(item)/1000.)
                startDateFormatted = startDateFormatted.strftime("%Y-%m-%d %H:%M:%S")
                startDatesFormatted.append(startDateFormatted) 
            self.worksheet.write_string('B1', 'StartDate')
            self.worksheet.write_column('B2', startDatesFormatted)
            col_width = max(map(len, startDatesFormatted)) + 2
            self.worksheet.set_column('B:B', col_width)
            #write vehicle column
            vehicles = [str(item['vehicle']) for item in dbFilePaths]
            self.worksheet.write_string('C1', 'Vehicle')
            self.worksheet.write_column('C2', vehicles)
            col_width = max(map(len, vehicles)) + 2
            self.worksheet.set_column('C:C', col_width)
            #write filenames column
            filenameswithoutpath = [os.path.basename(item['path']) for item in dbFilePaths]
            self.worksheet.write_string('D1', 'FileName')
            self.worksheet.write_column('D2', filenameswithoutpath)
            col_width = max(map(len, filenameswithoutpath)) + 2
            self.worksheet.set_column('D:D', col_width)
        else:
            # In PC mode the filename and path are all that matter for each file
            file_names = [item['path'] for item in dbFilePaths]
            self.worksheet.write_string('A1', 'FileNameAndPath')
            self.worksheet.write_column('A2', file_names)
            col_width = max(map(len, file_names)) + 2
            self.worksheet.set_column('A:A', col_width)

    def CloseWorkbook(self):
        self.workbook.close()