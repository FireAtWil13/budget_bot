from pprint import pprint

import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

class sheets_api:
  def __init__(self):
    
  # Файл, полученный в Google Developer Console
    self.CREDENTIALS_FILE = 'budget.json'
    # ID Google Sheets документа (можно взять из его URL)
    self.spreadsheet_id = '1ivCzxf3_2VDCDZbC4df8-SpHYHFqez123f1AUyHHwks'
    self.sheets_ids = {"main":"0", "transactions":"1648771542", "bot":"1103218185"}
    
    # Авторизуемся и получаем service — экземпляр доступа к API
    self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
        self.CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
  
    self.out_categries_range = "tech!M:M"
    self.in_categries_range = "tech!N:N"
    self.outcome_range = "Транзакции!B:E"
    self.income_range = "Транзакции!G:J"
    # httpAuth = credentials.authorize(httplib2.Http())
    
    
    try:
      self.service = build('sheets', 'v4', credentials=self.credentials)
    except:
      DISCOVERY_SERVICE_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
      self.service = build('sheets', 'v4', credentials=self.credentials, discoveryServiceUrl=DISCOVERY_SERVICE_URL)
  # service = build('sheets', 'v4', http = httpAuth)
  
  def get_out_categories(self):
    out_categries_range = self.out_categries_range
    cat_values = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=out_categries_range).execute();
    cat_column = cat_values['values'][cat_values['values'].index([])+1:]
    categries = self.flatten(cat_column)
    return categries
  
  def get_in_categories(self):
    in_categries_range = self.in_categries_range
    cat_values = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=in_categries_range).execute();
    cat_column = cat_values['values'][cat_values['values'].index([])+1:]
    categries = self.flatten(cat_column)
    return categries

  def append_values(self, range_name, row, value_input_option = 'USER_ENTERED'):
    # range_name as bool - income = True
    if range_name:
      range_name = self.income_range
    else:
      range_name = self.outcome_range

    values = [row]
    body = {'values': values}
    result = self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()

  def get_out_transactions(self):
    outcome_range = self.outcome_range
    transaction_values = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=self.outcome_range).execute();
    transaction_columns = transaction_values['values'][transaction_values['values'].index([])+1:]
    # categries = self.flatten(cat_column)
    return transaction_columns
  
  def get_in_transactions(self):
    income_range = self.income_range
    transaction_values = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=self.income_range).execute();
    cat_column = transaction_values['values'][transaction_values['values'].index([])+1:]
    # categries = self.flatten(cat_column)
    return cat_column

  
  def flatten(self, l):
    return [item for sublist in l for item in sublist]
  
  



