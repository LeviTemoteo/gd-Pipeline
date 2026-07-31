from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from sheets.aggregation import LevelAggregator

def export_to_google_sheets():
    
    credentials_path = Path("credentials.json")
    
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

    credentials = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    client = gspread.authorize(credentials)
    spreadsheet = client.open("Extreme_Sheets")

    try:
        worksheet = spreadsheet.worksheet("GD Raw Data")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(title="GD Raw Data", rows=1000, cols=12)

    aggregator = LevelAggregator()
    aggregated_levels = aggregator.agregate_all()

    headers = [
        "Level ID",
        "Level Name",
        "Type",
        "Difficulty",
        "Completed",
        "Completion Date",
        "Attempts",
        "Tracked Attempts",
        "Playtime",
        "Current Best",
        "Worst Fail"
    ]

    rows = [headers]
    for level in aggregated_levels:
        rows.append(level.to_list())
    worksheet.clear()
    worksheet.update(rows)
    print("Database Exported.", end="\n\n")