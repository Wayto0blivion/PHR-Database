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

        return render_template('hdd_search.html', form=form, pagination=cur_result, count=count, quality_count=quality_count, user=current_user)

    return render_template('hdd_search.html', form=form, user=current_user)


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

