"""
For some reason you can't pass BaseQuery objects through methods like this.
download_current is nonfunctional but was good for testing.

Im not sure the above is true? Download verification search works fine.
"""

import flask_excel as excel
from flask import make_response, render_template, redirect, url_for
from . import db, sqlEngine, hddEngine, validEngine, aikenEngine
import pandas
from functools import wraps
from .models import User
from flask_login import current_user


def download_search(search, bind):
    engine = ''
    if bind == 'hddEngine':
        engine = hddEngine
    elif bind == 'sqlEngine':
        engine = sqlEngine
    elif bind == 'validEngine':
        engine = validEngine
    elif bind == 'aikenEngine':
        engine = aikenEngine
    else:
        print('No engine detected!')
        return

    with engine.connect() as connection:
        df = pandas.read_sql(search.statement, con=connection)

        # Drop the autoID column if it exists.
        if 'autoID' in df.columns:
            df = df.drop(columns=['autoID'])

        resp = make_response(df.to_csv(index=False))
        resp.headers["Content-Disposition"] = f"attachment; filename={ bind }_Export.csv"
        resp.headers["Content-Type"] = "text/csv"
        return resp





def user_permissions(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            permission_level = permission
            if permission_level == 'PC Tech' and current_user.pc_status:
                # print('Current PC Tech Status', current_user.pc_status)
                return f(*args, **kwargs)
            elif permission_level == 'Servers' and current_user.server_status:
                return f(*args, **kwargs)
            elif permission_level == 'Processing' and current_user.processing_status:
                # print('Current PC Tech Status', current_user.pc_status)
                return f(*args, **kwargs)
            elif permission_level == 'HDD' and current_user.hdd_status:
                return f(*args, **kwargs)
            elif permission_level == 'Validation' and current_user.validation_status:
                return f(*args, **kwargs)
            elif permission_level == 'QR Generation' and current_user.qr_generation:
                return f(*args, **kwargs)
            elif permission_level == 'Admin' and current_user.admin_status:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('views.home'))
        return decorated_function
    return decorator



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








