import pandas as pd
import json

def xlsx_to_rows(data, sheet_name):
    return pd.read_excel(data, sheet_name=sheet_name)

def rows_to_dict(dataframe):
    return { row[4]: [row[6], row[7]] for row in dataframe.values }

def xlsx_to_dict(data, sheet_name):
    return rows_to_dict(xlsx_to_rows(data, sheet_name))

def xlsx_to_json(data, sheet_name):
    return json.dumps(xlsx_to_dict(data, sheet_name), indent=4)
