import pandas as pd


def import_branches(excel_file):

    df = pd.read_excel(excel_file)

    return df
