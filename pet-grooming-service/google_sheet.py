import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

GOOGLE_SHEET_ID = "1DD9pUu9qU2SFe0mfHuMCJZjqyiWvopwcxXomof84s9k"
spreedsheet = client.open_by_key(GOOGLE_SHEET_ID)


def append_row(
    sheet_name: str,
    new_row: list,
):
    worksheet = spreedsheet.worksheet(sheet_name)
    worksheet.append_row(new_row, value_input_option="RAW")
