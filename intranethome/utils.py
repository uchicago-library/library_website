import pandas as pd
import json
from io import BytesIO

DEFAULT_SHEET="data1"

def xlsx_to_df(data, sheet_name=DEFAULT_SHEET):
    return pd.read_excel(BytesIO(data), sheet_name=sheet_name)


def xlsx_to_dict(data, sheet_name=DEFAULT_SHEET):
    return df_to_dict(xlsx_to_df(data, sheet_name))

def xlsx_to_json(data, sheet_name=DEFAULT_SHEET):
    return json.dumps(xlsx_to_dict(data, sheet_name), indent=4)

def handle_to_df(handle):
    output = pd.read_excel(handle, sheet_name=DEFAULT_SHEET)
    return output

def project(dataframe):
    try:
        cols = dataframe[['PublicationName',
                          'StandardNumber',
                          'YearStart',
                          'YearEnd']]
        return cols
    except KeyError:
        return pd.DataFrame()

def df_to_dict(dataframe):
    cols = project(dataframe)
    return { row["StandardNumber"] : [row["YearStart"], row["YearEnd"]]
             for row in dataframe.to_dict('records') }
    # return { row[4]: [row[6], row[7]] for row in dataframe.values }

def df_to_list(dataframe):
    cols = project(dataframe)
    return cols.values.tolist()

def handle_to_list(handle):
    return df_to_list(handle_to_df(handle))
