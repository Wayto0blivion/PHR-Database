from flask import Blueprint, render_template, flash, request, redirect, url_for, session
from sqlalchemy import desc
from sqlalchemy.sql.expression import cast, text
from sqlalchemy.types import Date
from flask_login import login_required, current_user
from .models import Production, DISKS, MasterVerificationLog, VALIDATION, SuperWiper_Drives
from . import db
# import pymysql as pms
from .forms import ProductionSearchForm, DateForm, KilldiskForm, SuperWiperForm
# from flask_wtf import FlaskForm
import website.helper_functions as hf
from datetime import datetime

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

    form = KilldiskForm()

    page = request.args.get('page', 1, type=int)

    if form.clear.data:
        session.clear()
        return redirect(url_for(request.endpoint))

    results = None
    count = None
    quality_count = None

    if form.validate_on_submit():
        session['select'] = form.select.data
        session['search'] = form.search.data
        session['start_date'] = str(form.startdate.data) if form.startdate.data else None
        session['end_date'] = str(form.enddate.data) if form.enddate.data else None

    select = session.get('select')
    search = session.get('search')
    start_date = session.get('start_date')
    end_date = session.get('end_date')

    query = DISKS.query
    filters = []

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())
        filters.append(DISKS.Finished.between(start_date, end_date))

    if select and search:
        if select == 'OrderNo':
            filters.append(DISKS.OrderNo.contains(search))
        if select == 'DiskSerial':
            filters.append(DISKS.DiskSerial.contains(search))
        if select == 'Host':
            filters.append(DISKS.Host.contains(search))

    if filters:
        query = query.filter(*filters)

    results = query.paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)
    count = query.count()
    quality_count = query.filter(DISKS.Success == '1', DISKS.Passes == '1', DISKS.Progress == '100').count()

    if form.downl.data and results:
        return hf.download_search(query, 'hddEngine')

    if not form.validate_on_submit() and not (select or start_date or end_date):
        return render_template('hdd_search.html', form=form, user=current_user)

    return render_template('hdd_search.html', form=form, pagination=results, count=count,
                           quality_count=quality_count, user=current_user, select=select,
                           search=search, start_date=start_date, end_date=end_date)


@searchviews.route('/pandas_search', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Processing')
def pandasSearch():
    form = ProductionSearchForm()
    page = request.args.get('page', 1, type=int)
    # search = request.args.get('date', None, type=str)
    # print(search)

    if form.clear.data:
        session.clear()
        redirect(url_for(request.endpoint))

    if form.validate_on_submit():
        session['production_select'] = form.select.data
        session['production_search'] = form.search.data

    if session.get('production_search'):
        result_query = Production.query.filter\
            (getattr(Production, session['production_select'])
             .like('%{}%'.format(session['production_search'])))
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
        result_query = MasterVerificationLog.query\
            .filter(MasterVerificationLog.Date.between(session['start_date'], session['end_date']))\
            .order_by(desc(MasterVerificationLog.Date))
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
        result_query = VALIDATION.query.filter(VALIDATION.Date.between(session['start_date'], session['end_date']))\
            .order_by(desc(VALIDATION.Date))
        cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
        count = result_query.count()

        if form.downl.data:
            return hf.download_search(result_query, 'hddEngine')

        return render_template('validation_table.html', form=form, pagination=cur_result, count=count, user=current_user)

    return render_template('validation_table.html', form=form, user=current_user)


@searchviews.route("/superwiper-search", methods=['GET', 'POST'])
@login_required
def superwiper_search():
    """
    Allows searching, displaying, and downloading results from the Super Wiper database.
    """

    # Initialize search form and data dictionary
    data = {
        "form": SuperWiperForm(),
        "results": None,
        "count": None,
        "pagination": None,
        "search": None,
        "start_date": None,
        "end_date": None,
    }

    page = request.args.get('page', 1, type=int)

    # Clear session if "Clear" button is pressed
    if data['form'].clear.data:
        session.clear()
        return redirect(url_for(request.endpoint))

    # Save search parameters to session on form submission
    if data['form'].validate_on_submit():
        session['search'] = data['form'].search.data
        session['start_date'] = str(data['form'].startdate.data) if data['form'].startdate.data else None
        session['end_date'] = str(data['form'].enddate.data) if data['form'].enddate.data else None

    # Retrieve session values for searching
    data["search"] = session.get('search')
    data["start_date"] = session.get('start_date')
    data["end_date"] = session.get('end_date')

    # Initialize the query and filters
    query = SuperWiper_Drives.query
    filters = []

    # Convert stored VARCHAR dates to proper Date format and filter
    if data["start_date"] and data["end_date"]:
        try:
            start_date = datetime.strptime(data["start_date"], '%Y-%m-%d')
            end_date = datetime.strptime(data["end_date"], '%Y-%m-%d')
            start_date = datetime.combine(start_date, datetime.min.time())
            end_date = datetime.combine(end_date, datetime.max.time())

            filters.append(
                text(f"STR_TO_DATE(driveerasedate, '%a %b %d %H:%i:%s %Y') BETWEEN '{start_date}' AND '{end_date}'")
            )

            print(f"Filtering results between {start_date} and {end_date}")

        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for(request.endpoint))

    # Ignore serial number search if empty
    if data["search"] and data["search"].strip():
        filters.append(SuperWiper_Drives.driveserial.contains(data["search"]))

    # Apply filters if any exist
    if filters:
        query = query.filter(*filters)

    # Count total results before pagination
    data["count"] = query.count()
    print(f"Result count: {data['count']}")

    # Paginate the query (✅ Fixed Pagination)
    pagination = query.paginate(page=page, per_page=50, error_out=False)

    # ✅ **Download Search Results When Button is Pressed**
    if data['form'].downl.data and pagination.items:
        return hf.download_search(query, 'superWiperEngine')

    # Ensure results display correctly in the template
    return render_template(
        'skeleton_superwiper_search.html',
        data=data,
        pagination=pagination,  # ✅ Fixed Pagination
        user=current_user
    )
