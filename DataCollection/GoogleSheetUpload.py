# Importing Google Sheet Connection
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

class GoogleSheet(object):
    def __init__(self, key, url):
        self.key = key
        self.url = url
        self.scope = ['https://spreadsheets.google.com/feeds',
                      'https://www.googleapis.com/auth/drive']
        self.sheet_id = None
        self.credentials = None
        self.workbooks = None

    def get_id(self):
        """
        This function will extract the Sheet ID required for the connection
        """
        urlString = self.url.lstrip("https://docs.google.com/spreadsheets/d/")
        sheet_id = urlString.split("/")[0]
        self.sheet_id = sheet_id

    def get_credentials(self):
        """
        Reading in the credentials from the json secret key.
        """
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.key, self.scope)
        self.credentials = credentials

    def connect(self):
        """
        This function will run all functions to obtain variables required for API call
        from user input. Afterward, we will establish a connection to the Google Sheet
        """
        self.get_id()
        self.get_credentials()
        connection = gspread.authorize(self.credentials)
        workbook = connection.open_by_key(self.sheet_id)
        self.workbook = workbook



    def iter_pd(self, df):
        """
        Converting data type of the Pandas Dataframe
        """
        for val in df.columns:
            yield val
        for row in df.to_numpy():
            for val in row:
                if pd.isna(val):
                    yield ""
                else:
                    yield val

    def push_to_gsheet(self, pandas_df, sheetname="Sheet1", clear=True):
        """
        Updates all values in a workbook to match a pandas dataframe
        """
        sheet = self.workbook.worksheet(sheetname)

        if clear:
            sheet.clear()
        else:
            pass
        (row, col) = pandas_df.shape
        cells = sheet.range("A1:{}".format(gspread.utils.rowcol_to_a1(row + 1, col)))
        for cell, val in zip(cells, self.iter_pd(pandas_df)):
            cell.value = val
        sheet.update_cells(cells)



if __name__ == '__main__':
    testconnect = GoogleSheet("../DataCollection/SecretKeys/tableaucoviddemo-f9907cac4544.json", "https://docs.google.com/spreadsheets/d/1no4IXxDRTBqvkm59CGLSLDz7SomSeCbdfpcRaNtQ83I/edit#gid=0")
    testconnect.connect()
    pass
