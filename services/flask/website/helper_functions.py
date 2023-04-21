"""
For some reason you can't pass BaseQuery objects through methods like this.
download_current is nonfunctional but was good for testing.

Im not sure the above is true? Download verification search works fine.
"""

import flask_excel as excel
from flask import make_response
from . import db, sqlEngine, hddEngine, validEngine
import pandas


def download_search(search, bind):
    engine = ''
    if bind == 'hddEngine':
        engine = hddEngine
    elif bind == 'sqlEngine':
        engine = sqlEngine
    elif bind == 'validEngine':
        engine = validEngine
    else:
        print('No engine detected!')
        return

    with engine.connect() as connection:
        df = pandas.read_sql(search.statement, con=connection)

        resp = make_response(df.to_csv(index=False))
        resp.headers["Content-Disposition"] = f"attachment; filename={ bind }_Export.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp



# Old Download function, pre Flask upgrade
# def download_hdd_search(search):
#     column_names = search.statement.columns.keys()
#     print(column_names)
#     results = search.all()
#     return excel.make_response_from_query_sets(results, column_names=column_names[1:], file_type="csv")


# Old Download function, pre Flask upgrade
# def download_verification_search(search):
#     column_names = search.statement.columns.keys()
#     print(column_names)
#     results = search.all()
#     return excel.make_response_from_query_sets(results, column_names=column_names, file_type="csv")








