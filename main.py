import bot

with open("./bot_token.txt", "r") as bot_token:
  token = bot_token.read()

bot = bot.BudgetBot(token)


# import sheets
# sheets = sheets.sheets_api()
# sheets.append_values(True, ['21.07.23','12345','Test','Другое'])

# from __future__ import print_function

# from pprint import pprint

# import httplib2
# import apiclient.discovery
# from oauth2client.service_account import ServiceAccountCredentials
# from googleapiclient.discovery import build


# # Файл, полученный в Google Developer Console
# CREDENTIALS_FILE = 'budget.json'
# # ID Google Sheets документа (можно взять из его URL)
# # spreadsheet_id = '1gqZ6Yo0BGdpmwrxRoC9ksO90P9ozOtoLZspBiCetX4I'
# spreadsheet_id = '1ivCzxf3_2VDCDZbC4df8-SpHYHFqez123f1AUyHHwks'

# sheets_ids = {"main":"0", "transactions":"1648771542", "bot":"1103218185"}

# # Авторизуемся и получаем service — экземпляр доступа к API
# credentials = ServiceAccountCredentials.from_json_keyfile_name(
#     CREDENTIALS_FILE,
#     ['https://www.googleapis.com/auth/spreadsheets',
#      'https://www.googleapis.com/auth/drive'])
# # httpAuth = credentials.authorize(httplib2.Http())


# try:
#   service = build('sheets', 'v4', credentials=credentials)
# except:
#   DISCOVERY_SERVICE_URL = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
#   service = build('sheets', 'v4', credentials=credentials, discoveryServiceUrl=DISCOVERY_SERVICE_URL)
# # service = build('sheets', 'v4', http = httpAuth)

# # values = service.spreadsheets().values().get(
# #     spreadsheetId=spreadsheet_id,
    
# #     range='B24:E36',
# #     # majorDimension='COLUMNS'
# # ).execute()
# # request = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges="bot!A:A", includeGridData=False).execute()
# # values['values'].index([])

# def flatten(l):
#     return [item for sublist in l for item in sublist]

# # categries_range = "bot!A:A"
# # cat_values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=categries_range).execute();
# # cat_column = cat_values['values'][cat_values['values'].index([])+1:]
# # categries = flatten(cat_column)

# # pprint([item for sublist in cat_column for item in sublist])
# # pprint(cat_values['values'][cat_values['values'].index([])+1:])


# outcome_range = "Транзакции!B:B"
# out_values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range="Транзакции!B:E").execute();
# pprint(out_values)
# out_column = out_values['values'][out_values['values'].index([])+1:]
# pprint(flatten(out_column))


# income_range = "Транзакции!G:G"
# in_values = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=income_range).execute();
# in_column = in_values['values'][in_values['values'].index([])+1:]
# pprint(flatten(in_column))
# # pprint(out_values['values'])
# value_input_option = 'USER_ENTERED'
# range_name = "Транзакции!B:E"
# values = [
#     [
#       '21.07.2023', '305,00', 'Убер(Лена к Рите)', 'Транспорт'
#     ],
#     # Additional rows ...
# ]
# body = {
#     'values': values
# }
# # result = service.spreadsheets().values().append(
# #     spreadsheetId=spreadsheet_id, range=range_name,
# #     valueInputOption=value_input_option, body=body).execute()
# print(f"{(result.get('updates').get('updatedCells'))} cells appended.")

# def append_values(spreadsheet_id, range_name, value_input_option = 'USER_ENTERED',
#                   _values):
#     """
#     Creates the batch_update the user has access to.
#     Load pre-authorized user credentials from the environment.
#     TODO(developer) - See https://developers.google.com/identity
#     for guides on implementing OAuth2 for the application.
#         """
#     creds, _ = google.auth.default()
#     # pylint: disable=maybe-no-member
#     try:
#         service = build('sheets', 'v4', credentials=creds)

#         values = [
#             [
#                 # Cell values ...
#             ],
#             # Additional rows ...
#         ]
#         body = {
#             'values': values
#         }
#         result = service.spreadsheets().values().append(
#             spreadsheetId=spreadsheet_id, range=range_name,
#             valueInputOption=value_input_option, body=body).execute()
#         print(f"{(result.get('updates').get('updatedCells'))} cells appended.")
#         return result

#     except HttpError as error:
#         print(f"An error occurred: {error}")
#         return error

# categries = [item for sublist in out_column for item in sublist]