from functools import reduce
from io import BytesIO

import pandas as pd
from django.core.files.base import ContentFile
from wagtail.documents import get_document_model

from base.result import bind, error, ok, rmap
from library_website.settings import AGS_DEFAULT_SHEET

# Retrieving XLSX from a POST parameter


def request_to_xlsx(request):
    """
    Reads binary XLSX data out of the POST data.

    Args:
        request: An HTTP request.

    Returns:
        binary XLSX data
    """
    if request.method == "POST" and "uploadFile" in request.FILES:
        upload_file = request.FILES["uploadFile"]
        with upload_file.open(mode="rw") as f:
            xlsx_data = f.read()
            return xlsx_data
    else:
        return b""


# XLSX validation/transformation


def xlsx_to_df_exn(xlsx, sheet_name=AGS_DEFAULT_SHEET):
    """
    Converts binary XLSX to a pandas dataframe.  Not
    exception-safe.

    Args:
        xlsx: Binary XLSX data.
        sheet_name: expected name of the XLSX spreadsheet

    Returns:
        A pandas dataframe containing the information in the sheet
        named as specified in the input.
    """
    return pd.read_excel(BytesIO(xlsx), sheet_name=sheet_name)


def xlsx_to_df(xlsx):
    """
    Like xlsx_to_df_exn, but returns the output in monadic result
    format.

    Args:
        xlsx: Binary XLSX data.

    Returns:
        Success when the XLSX can be converted to a dataframe;
        failure otherwise.
    """
    try:
        df = xlsx_to_df_exn(xlsx)
        return ok(df)
    except ValueError:
        msg = "Invalid spreadsheet: the worksheet must " "be named 'data1'"
        return error(msg)


def df_to_dict_exn(df):
    """
    Converts pandas dataframe to a lookup table for determining
    journal coverage.  Not exception-safe.

    Args:
        df: Spreadsheet as a pandas dataframe.

    Returns:
        A dictionary with ISSN strings as keys and string lists
        indicating journal coverage as values.
    """
    return {
        row["StandardNumber"]: [row["YearStart"], row["YearEnd"]]
        for row in df.to_dict("records")
    }


required_columns = [
    "PublicationName",
    "StandardNumber",
    "YearStart",
    "YearEnd",
]


def validate_dataframe(df):
    """
    Performs all necessary validations on the input
    spreadsheet-as-dataframe.

    Args:
        df: Spreadsheet as a pandas dataframe.

    Returns:
        The spreadsheet, in monadic result format.
    """

    def contains_column(name):
        def inner(df):
            if name in df:
                return ok(df)
            else:
                msg = (
                    "Invalid spreadsheet: required column "
                    "name '%s' is missing." % name
                )
                return error(msg)

        return inner

    def reducer(validated, next_col):
        return bind(validated, contains_column(next_col))

    return reduce(reducer, required_columns, ok(df))


def df_to_dict(df):
    """
    Like df_to_dict_exn, but returns the output in monadic result
    format.

    Args:
         df: Spreadsheet as pandas dataframe

    Returns:
        Lookup table for journal coverage, in monadic result
        format.
    """
    return rmap(df_to_dict_exn, validate_dataframe(df))


def validate_xlsx(xlsx):
    """
    Like validate_dataframe, except with an XLSX binary as an input
    format.  Returns the output in monadic result format.

    Args:
        xlsx: XLSX binary data.

    Returns:
        Success on the empty string or fully valid XLSX data;
        failure otherwise.
    """
    if not (xlsx):
        return ok(xlsx)
    else:
        df_result = xlsx_to_df(xlsx)
        match bind(df_result, validate_dataframe):
            case {"ok": _}:
                return ok(xlsx)
            case {"error": msg}:
                return error(msg)
            case other:
                msg = "invalid result value: %s" % str(other)
                raise Exception(msg)


def handle_to_df_exn(handle):
    """
    Read binary XLSX data in from a file handle and output pandas
    dataframe.  Not exception safe.

    Args:
        handle: File handle.

    Returns:
        Spreadsheet as a pandas dataframe.
    """
    output = pd.read_excel(handle, sheet_name=AGS_DEFAULT_SHEET)
    return output


def doc_to_dataframe_exn(doc):
    """
    Convert XLSX Wagtail Document into pandas dataframe.

    Args:
        doc: Wagtail document object.

    Returns:
        Spreadsheet as a pandas dataframe.
    """
    with doc.file.open() as f:
        return handle_to_df_exn(f)


# Preview table generation


def df_to_list(df):
    """
    Convert spreadsheet as pandas dataframe to list of rows to be
    passed into template context.

    Args:
        df: Spreadsheet as a pandas dataframe.

    Returns:
        List of lists, each row represents a column in the
        spreadsheet preview.
    """

    def project(df):
        try:
            cols = df[required_columns]
            return cols
        except KeyError:
            return pd.DataFrame()

    cols = project(df)
    return cols.values.tolist()


def indicate_diff(issn, issns1, issns2, all_rows):
    """
    For a given issn, determine whether it has been deleted from
    the first list, added to the second list, or is present in both
    lists.

    Args:
        issn: An ISSN string.
        issns1: A list of the old ISSN strings.
        issns2: A list of the updated ISSN strings.

    Returns:
        A tuple containing a minus, plus, or empty string,
        followed by the string for a red or green HTML style
        attribute, followed by the row containing issn.
    """
    minus_color = "#fce6e9"
    plus_color = "#e4f7ea"

    def styleify(hex_string):
        return "background-color:  %s;" % hex_string

    def find_by_issn(issn, rows):
        return next((row for row in rows if row[1] == issn), None)

    if issn in issns1 and issn not in issns2:
        return ("-", styleify(minus_color), find_by_issn(issn, all_rows))
    elif issn in issns2 and issn not in issns1:
        return ("+", styleify(plus_color), find_by_issn(issn, all_rows))
    else:
        return ("", "", find_by_issn(issn, all_rows))


def diff_rows(old_rows, new_rows):
    """
    Compute visual diff representation that displays +/- changes
    between two spreadsheet previews.

    Args:
        old_rows: Old spreadsheet preview.
        new_rows: New spreadsheet preview.

    Returns:
        A tuple containing the spreadsheet preview augmented with
        diffing information.
    """
    issns1 = [row[1] for row in old_rows]
    issns2 = [row[1] for row in new_rows]
    enumerated = list(enumerate(issns2)) + list(enumerate(issns1))
    sorted_them = sorted(enumerated, key=lambda x: x[0])
    interleaved = [x for (_, x) in sorted_them]
    unioned_issns = list(dict.fromkeys(interleaved))
    unioned_rows = old_rows + new_rows
    reds = len(set(issns1) - set(issns2))
    greens = len(set(issns2) - set(issns1))
    return (
        reds,
        greens,
        [indicate_diff(issn, issns1, issns2, unioned_rows) for issn in unioned_issns],
    )


def pad_with_empties(rows):
    """
    Extend simple spreadsheet preview into vacuous diff format
    spreadsheet preview, showing no diffs.

    Args:
        rows: Spreadsheet preview as list of string values
        for each row.

    Returns:
        A vacuous/blank diff format spreadsheet preview.
    """
    return [("", "table-active", row) for row in rows]


def doc_to_rows_exn(doc):
    """
    Load spreadsheet as pandas dataframe from a Wagtail Document.
    Not exception-safe.

    Args:
        Spreadsheet as Wagtail Document.

    Returns:
        Spreadsheet as Pandas dataframe.
    """
    df = doc_to_dataframe_exn(doc)
    return df_to_list(df)


# Reading/Writing Wagtail Documents


def bool_to_msg(confirm):
    """
    Helper function converting boolean to message that appears
    after the confirmation window.

    Args:
        confirm: Boolean representing whether the user confirmed the
        request.

    Returns:
        Message about the database being updated, or the empty
        string if the input is False.
    """
    if confirm:
        return "Updating AGS spreadsheet in Wagtail database..."
    else:
        return ""


def create_document(filename):
    """
    (Curried) helper function to create a new Wagtail Document.

    Args:
        filename: Title to be given to Wagtail Document.
        bytz: XLSX binary data to be saved as a Wagtail Document.

    Returns: True if there already was a file in Wagtail documents
        with title filename; False otherwise.
    """

    def inner(bytz):
        if bytz:
            D = get_document_model()
            try:
                ags_xlsx = D.objects.get(title=filename)
                ags_xlsx.delete()
            except D.DoesNotExist:
                pass
            doc = D(title=filename)
            doc.file.save(filename, ContentFile(bytz))
            return True
        else:
            return False

    return inner


def retrieve_document(mod, title):
    """
    Look a Wagtail Document up by title; return it in monadic
    result format.

    Args:
        mod: Wagtail Document Model.
        title: String indicating title to be queried.

    Returns: First document found, in the success case; error message,
        in the failure case.
    """
    docs_by_name = mod.objects.filter(title=title)
    sort_em = sorted(docs_by_name, key=lambda doc: doc.created_at, reverse=True)
    if sort_em:
        return ok(sort_em[0])
    else:
        # this error message is only used in the ags/js view
        return error("No AGS spreadsheet present in Wagtail database.")


def delete_document_exn(mod, title):
    """
    Delete all Wagtail Documents matching input title from the
    database.

    Args:
        mod: Wagtail Document Model.
        title: String indicating title of document to be deleted.
    """
    docs_by_name = mod.objects.filter(title=title)
    [d.delete() for d in docs_by_name]


# Generating Javascript for /js view


def doc_to_dict_exn(doc):
    """
    Convert Wagtail Document to dictionary representing a lookup
    table for journal coverages.

    Not exception-safe; should only be used with input that has already
    been validated by validate_xlsx or validate_dataframe.

    Args:
        doc: A Wagtail Document.

    Returns:
        Dictionary lookup table for journal coverages.
    """
    df = doc_to_dataframe_exn(doc)
    return df_to_dict_exn(df)
