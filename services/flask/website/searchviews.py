from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from flask_login import login_required, current_user
from .models import Production, DISKS, MasterVerificationLog, VALIDATION
from . import db
# import pymysql as pms
from .forms import ProductionSearchForm, DateForm
# from flask_wtf import FlaskForm
import website.helper_functions as hf

searchviews = Blueprint('searchviews', __name__)
ROWS_PER_PAGE = 50


# @searchviews.route('/search_test', methods=['GET', 'POST'])
# def searchtest():
#     """
#     Gives search results for partial searches.
#     Currently, only checks for partial searches on "orderNo" column
#
#     use getattr to get the attribute of Production (like orderNo) to call the results from select_field
#     """
#     form = ProductionSearchForm(request.form)
#     if request.method == 'POST':
#         select_field  = form.select.data
#         #print(select_field)
#         search_string = form.search.data
#         #print(search_string,select_field)
#         if search_string == '':
#             results = db.session.query(Production).limit(5000)
#         else:
#             kwargs = {str(select_field):str(search_string)}
#             results = Production.query.filter(Production.orderNo.like(**kwargs)).all()
#
#         if not results:
#             flash('No results found!', category='error')
#             print('if not: ' + form)
#             return redirect(url_for('.searchtest', form=form))
#         else:
#             return render_template('search.html', form=form, result=results, user=current_user)
#
#
#
#     else:
#     #    return redirect(url_for('.searchtest', form=form, user=current_user))
#         return render_template('search.html', form=form, user=current_user)



#Testing. For basic search methods. Paired with below
# @searchviews.route('/search', methods=['GET', 'POST'])
# def search_func():
#     '''
#
#     '''
#     search = ProductionSearchForm(request.form)
#     if request.method == 'POST':
#         return search_results(search)
#
#     return render_template('search.html', form=search, user=current_user)

# @searchviews.route('/searchresults')
# def search_results(search):
#     results = []
#     search_string = search.data['search']
#     print("search_string: " + search_string)
#
#     if search.data['search'] == '':
#         qry = db.session.query(Production)
#         results = qry.limit(5000)
#
#     if not results:
#         flash('No results found', category='error')
#         return redirect(url_for('.search_func', form=search, user=current_user))
#     else:
#         #display results
#         return render_template('search.html', form=search, result=results, user=current_user)


@searchviews.route('/hdd_search', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('PC Tech')
def hdd_search():
    """
    For paginating and displaying search results from the DISKS table.
    Uses session variables to pass information.

    Requires:
    website.helper_functions.py for download function.
    download function takes an unfinished query variable,
    but is internal.
    """

    form = DateForm()

    page = request.args.get('page', 1, type=int)

    if form.clear.data:
        session.clear()
        return redirect(url_for(request.endpoint))

    if form.validate_on_submit():
        session['start_date'] = str(form.startdate.data)
        session['end_date'] = str(form.enddate.data)

    if session.get('start_date'):
        result_query = DISKS.query.filter(DISKS.BatchStarted.between(session['start_date'], session['end_date']))
        cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
        count = result_query.count()

        quality_count = result_query.filter(DISKS.Success == '1', DISKS.Passes == '1', DISKS.Progress == '100').count()

        if form.downl.data:
            '''
            For some reason, the "OS" column was used as the first column.
            Skipped first column(OS) with [1:]. Doesn't display in download.
            
            FUTURE EDIT: The download function works by matching variable names to the 
            names of the SQL columns. Therefore, model variable names must match its corresponding
            column in the SQL table. The "OS" column must be skipped bc it is impossible to match that
            column name in python (OS is a reserved variable). Luckily, it moved the problem column
            to the front, so it can easily be skipped.
            
            '''
            return hf.download_search(result_query, 'hddEngine')

            # df = pandas.read_sql(result_query.statement, con=hddEngine.connect())
            #
            # resp = make_response(df.to_csv(index=False))
            # resp.headers["Content-Disposition"] = "attachment; filename=Production_Export.csv"
            # resp.headers["Content-Type"] = "text/csv"
            # return resp

            # return hf.download_hdd_search(result_query)

        return render_template('hdd_search.html', form=form, pagination=cur_result, count=count, quality_count=quality_count, user=current_user)

    return render_template('hdd_search.html', form=form, user=current_user)


'''
@searchviews.route('/pandas_search', methods=['GET', 'POST'])
@login_required
def pandasSearch():
    prodForm = ProductionSearchForm()
    if request.method == 'POST':
        form = request.form
        search_term = form['search']
        select_term = form['select']

        #dbConnection = sqlEngine.connect()
        #sql_query = 'SELECT `Unit #` AS "Unit #",`Product Name` AS "Product Name", "NA" AS "HDD MFG", "NA" AS "HDD Serial #", `Manufacturer` AS "Manufacturer", `Model` AS "Model", `Serial Number` AS "Serial #", `Asset` AS "Asset", `Year Manufactured` AS "Year Manufactured", `Processor` AS Processor, `Speed` AS Speed, `RAM (GB)` AS RAM, `Media` AS Media, `COA` AS COA, `Form Factor` AS "Form Factor", "N/A" AS "HDD (GB)", `Test Result Codes` AS "TEST RESULT CODES (SEE TRANSLATIONS)", `Sale Category` AS "Sale Category" FROM Production'

        #df = pandas.read_sql(sql_query, dbConnection)
        #if select_term == 'orderNo':
        #    select_term = 'Order Number'
        #elif select_term == 'productName':
        #    select_term = 'Product Name'
        #elif select_term == 'serialNo':
        #    select_term = 'Serial Number'
        #elif select_term == 'date':
        #    select_term = 'Date'

        #formats string so that it can be passed to filter
        #print(select_term)
        #f = getattr(Production, select_term)
        #search_format = {select_term: search_term}
        #results_str = str(Production.query.filter_by(**search_format).all())
        #result_builder = 'SELECT Production.* FROM Production WHERE `{0}` LIKE "%{1}%"'.format(select_term, search_term)
        #results = Production.query.filter_by(**search_format).all()




        results = Production.query.filter(getattr(Production, select_term).like('%{}%'.format(search_term)))
        #print(str(results.statement))
        #df_from_results = pandas.read_sql(Production.query.filter(getattr(Production, select_term).like('%{}%'.format(search_term))).statement, dbConnection).to_html(classes='table table-dark')
        #results_df_html = df_from_results.to_html(classes='table')
        #print(result_builder)
        #results = result_builder
        #results = db.session.execute(result_builder)
        #print(results_str)
        #results_string = str(results)
        #print(str(results))
        #df = pandas.read_sql(results.statement, dbConnection)
        #mystring  = results.sub(r"&lrm;", "", results)
        #mystring  = results.sub(r"&zwnj;", "", results)
        #df_html = df.to_html(classes='table')
        #print(str(results))
        #if prodForm.validate_on_submit():
        #    print('validated!')
        #result_from_records = pandas.DataFrame.from_records(results)
        #dbConnection = sqlEngine.connect()
        #result_from_records = pandas.read_sql_query(results.statement, dbConnection)
        #dbConnection.close()
        #result_from_records = result_from_records.to_html(classes='table table-dark')



        if prodForm.downl.data:
            print('Download!')
            if select_term == 'orderNo':
                select_term = 'Order Number'
            elif select_term == 'productName':
                select_term = 'Product Name'
            elif select_term == 'serialNo':
                select_term = 'Serial Number'
            elif select_term == 'date':
                select_term = 'Date'

            query_sets = db.session.execute('SELECT `Unit #` AS "Unit #",`Product Name` AS "Product Name", "NA" AS "HDD MFG", "NA" AS "HDD Serial #", `Manufacturer` AS "Manufacturer", `Model` AS "Model", `Serial Number` AS "Serial #", `Asset` AS "Asset", `Year Manufactured` AS "Year Manufactured", `Processor` AS Processor, `Speed` AS Speed, `RAM (GB)` AS RAM, `Media` AS Media, `COA` AS COA, `Form Factor` AS "Form Factor", "N/A" AS "HDD (GB)", `Test Result Codes` AS "TEST RESULT CODES (SEE TRANSLATIONS)", `Sale Category` AS "Sale Category" FROM Production WHERE `{0}` LIKE "%{1}%"'.format(select_term, search_term))
            column_names = ["Unit #", 'Product Name', "HDD MFG", "HDD Serial #", 'Manufacturer', 'Model', 'Serial #', "Asset", 'Year Manufactured', 'Processor', 'Speed', 'RAM', 'Media', 'COA', 'Form Factor', 'HDD (GB)', "TEST RESULT CODES (SEE TRANSLATIONS)", 'Sale Category']
            return excel.make_response_from_query_sets(query_sets, column_names, "csv")
        else:
            print('No Download!')


        result_count = f"Search returned {results.count()} results"



        return render_template('search.html', form=prodForm, results=results, count=result_count, user=current_user)
    else:
        return render_template('search.html', form=prodForm, user=current_user)
'''


#def query_db(select, search):
#    f = getattr(Production, select)
#    q = Production.query.filter((select))
#    return q.all()


@searchviews.route('/pandas_search', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Processing')
def pandasSearch():
    form = ProductionSearchForm()
    page = request.args.get('page', 1, type=int)

    if form.clear.data:
        session.clear()
        redirect(url_for(request.endpoint))

    if form.validate_on_submit():
        session['production_select'] = form.select.data
        session['production_search'] = form.search.data

    if session.get('production_search'):
        result_query = Production.query.filter\
            (getattr(Production, session['production_select']).like\
             ('%{}%'.format(session['production_search'])))
        cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
        count = result_query.count()

        if form.downl.data:

            return hf.download_search(result_query, 'sqlEngine')

            # df = pandas.read_sql(result_query.statement, con=sqlEngine.connect())
            #
            # resp = make_response(df.to_csv(index=False))
            # resp.headers["Content-Disposition"] = "attachment; filename=Production_Export.csv"
            # resp.headers["Content-Type"] = "text/csv"
            # return resp

        return render_template('search.html', form=form,
                               pagination=cur_result, count=count, user=current_user)

    return render_template('search.html', form=form, user=current_user)

# ------------------------------------------------------------------------------------------------------


@searchviews.route('master_validation', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Validation')
def master_validation():
    """
    For searching and displaying results from the Master Verification Log.

    Requires:
    helper_functions.py imported as hf


    """

    form = DateForm()

    page = request.args.get('page', 1, type=int)

    if form.clear.data:
        session.clear()
        return redirect (url_for(request.endpoint))

    if form.validate_on_submit():
        session['start_date'] = str(form.startdate.data)
        session['end_date'] = str(form.enddate.data)

    if session.get('start_date'):
        result_query = MasterVerificationLog.query.filter(MasterVerificationLog.Date.between(session['start_date'], session['end_date']))
        cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
        count = result_query.count()

        if form.downl.data:
            return hf.download_search(result_query, 'validEngine')

        return render_template('master_validation_table.html', form=form, pagination=cur_result, count=count, user=current_user)

    return render_template('master_validation_table.html', form=form, user=current_user)

# ----------------------------------------------------------------------------------------------------------------------

@searchviews.route('hdd_validation_table', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Validation')
def hdd_validation():
    """
    For searching and displaying results from the Master Verification Log.

    Requires:
    helper_functions.py imported as hf


    """
    form = DateForm()

    page = request.args.get('page', 1, type=int)

    if form.clear.data:
        session.clear()
        return redirect (url_for(request.endpoint))

    if form.validate_on_submit():
        session['start_date'] = str(form.startdate.data)
        session['end_date'] = str(form.enddate.data)

    if session.get('start_date'):
        result_query = VALIDATION.query.filter(VALIDATION.Date.between(session['start_date'], session['end_date']))
        cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
        count = result_query.count()

        if form.downl.data:
            return hf.download_search(result_query, 'hddEngine')

        return render_template('validation_table.html', form=form, pagination=cur_result, count=count, user=current_user)

    return render_template('validation_table.html', form=form, user=current_user)

