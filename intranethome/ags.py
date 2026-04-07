from django.core.files.base import ContentFile
import pandas as pd
import json
from io import BytesIO
from wagtail.documents import get_document_model
from functools import reduce


############ monadic error handling utility functions ################


def ok(x):
    return { "ok": x }


def error(msg):
    return { "error": msg }


def rmap(f, result):
    match result:
        case { "ok": x }:
            return ok(f(x))
        case { "error": msg }:
            return { "error": msg }
        case other:
            msg = "invalid result value: %s" % str(other)
            raise Exception(msg)


def bind(result, k):
    match result:
        case { "ok": x }:
            return k(x)
        case { "error": msg }:
            return { "error": msg }
        case other:
            msg = "invalid result value: %s" % str(other)
            raise Exception(msg)


#################### XLSX data transformation ########################


DEFAULT_SHEET="data1"


def xlsx_to_df_exn(data, sheet_name=DEFAULT_SHEET):
    return pd.read_excel(BytesIO(data), sheet_name=sheet_name)


def xlsx_to_df(xlsx):
    try:
        df = xlsx_to_df_exn(xlsx)
        return(ok(df))
    except ValueError:
        msg = ("Invalid spreadsheet: the worksheet must "
               "be named 'data1'")
        return error(msg)


def df_to_dict_exn(df):
    return { row["StandardNumber"]:
             [ row["YearStart"], row["YearEnd"] ]
             for row in df.to_dict('records') }


required_columns = [
    "PublicationName",
    "StandardNumber",
    "YearStart",
    "YearEnd",
]

def validate_dataframe(df):
    def contains_column(name):
        def inner(df):
            if name in df:
                return ok(df)
            else:
                msg = ("Invalid spreadsheet: required column "
                       "name '%s' is missing." % name)
                return error(msg)
        return inner
    def reducer(validated, next_col):
        return bind(validated, contains_column(next_col))
    return reduce(reducer, required_columns, ok(df))


def df_to_dict(df):
    return rmap(df_to_dict_exn, validate_dataframe(df))


def request_to_xlsx(request):
    if request.method == 'POST' and 'uploadFile' in request.FILES:
        upload_file = request.FILES['uploadFile']
        with upload_file.open(mode="rw") as f:
            xlsx_data = f.read()
            return xlsx_data
    else:
        return b""


def validate_xlsx(xlsx):
    if not(xlsx):
        return ok(xlsx)
    else:
        df_result = xlsx_to_df(xlsx)
        match bind(df_result, validate_dataframe):
            case { "ok": _ }:
                return ok(xlsx)
            case { "error": msg }:
                return error(msg)
            case other:
                msg = "invalid result value: %s" % str(other)
                raise Exception(msg)


# def xlsx_to_dict(data, sheet_name=DEFAULT_SHEET):
#     return df_to_dict(xlsx_to_df(data, sheet_name))


# def xlsx_to_json(data, sheet_name=DEFAULT_SHEET):
#     return json.dumps(xlsx_to_dict(data, sheet_name), indent=4)


# def handle_to_df(handle):
#     output = pd.read_excel(handle, sheet_name=DEFAULT_SHEET)
#     return output
        

def df_to_list(dataframe):
    def project(dataframe):
        try:
            cols = dataframe[required_columns]
            return cols
        except KeyError:
            return pd.DataFrame()
    cols = project(dataframe)
    return cols.values.tolist()


def handle_to_list(handle):
    df = handle_to_df(handle)
    validated = validate_dataframe(df)
    return rmap(df_to_list, validated)


def document_model_to_doc(mod, title):
    docs_by_name = mod.objects.filter(title=title)
    sort_em = sorted(
        docs_by_name,
        key=lambda doc: doc.created_at,
        reverse=True
    )
    if sort_em:
        return ok(sort_em[0])
    else:
        msg = "No AGS spreadsheet currently uploaded."
        return error(msg)


def document_model_to_rows(mod, title):
    doc_result = document_model_to_doc(mod, title)
    def compute_rows(doc):
        with doc.file.open() as f:
            return handle_to_list(f)
    rows = bind(doc_result, compute_rows)
    return rows


def create_document(filename):
    def inner(bytz):
        if bytz:
            D = get_document_model()
            try:
                ags_xlsx = D.objects.get(title=filename)
                ags_xlsx.delete()
                update_msg = ("Updating AGS spreadsheet "
                              "in Wagtail Documents...")
            except D.DoesNotExist:
                update_msg = ("Adding new AGS spreadsheet "
                              "to Wagtail Documents...")
            doc = D(title=filename)
            doc.file.save(filename, ContentFile(bytz))
            return (bytz, update_msg)
        else:
            return (bytz, "")
    return inner



