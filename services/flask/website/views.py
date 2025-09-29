from flask import (Flask, Blueprint, render_template, flash, request, jsonify, session,
                   url_for, Response, send_file, redirect)
from flask_login import login_required, current_user
from flask_sqlalchemy import Pagination
from sqlalchemy import exc, desc, func, and_, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
# from sqlalchemy import create_engine
from .models import (Note, imported_sheets, VALIDATION, MasterVerificationLog, BATCHES, Customers, Lots, Units,
                     Units_Devices, UnitsDevicesSearch, Server_AddOns, Searches_Addons, Network_Price_Data,
                     Mobile_Boxes, Mobile_Pallets, Mobile_Box_Devices, Mobile_Weights)
from . import db, sqlEngine, validEngine, aikenEngine, app, qrcode
import json
import flask_excel as excel
import pandas as pandas
import seaborn as sns
import matplotlib.pyplot as plt
# import pymysql as pms
from .forms import (ValidationEntryForm, ImportForm, CustomerEntryForm, CustomerSearchForm, AikenProductionForm,
                    AikenDeviceSearchForm, Server_AddOn_Form, NetworkPricingSearchForm)
from datetime import date, datetime, timedelta
import numpy as np
import website.helper_functions as hf
from werkzeug.utils import secure_filename
import flask_qrcode
from io import BytesIO

views = Blueprint('views', __name__)

ROWS_PER_PAGE = 50


# --------------------------------------------------------------------------------------


@views.route('/site-map', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Admin')
def site_map():
    """
    For generating a site map of all available views.

    Requires:
        has_no_empty_params(rule)
    """
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules that can't be navigated to in the browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
            # links is now a list of url, endpoint tuples
    # print(links)
    return render_template('site_mapper.html', links=links, user=current_user)


def has_no_empty_params(rule):
    """
    Function separated from site_map to handle functions that require parameters.
    """
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


# ----------------------------------------------------------------------------------------


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    session.clear()
    # print(current_user.email)

    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note Added!', category='success')

    return render_template("home.html", user=current_user)


# Testing. For removing custom notes
@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


# -----------------------------------------------------------------------------------------------
# For adding sheet id to Production table, and removing sheetName if import fails
@views.route('/pandas_import', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Processing')
def safeimport():
    form = ImportForm()

    frame = None

    shape = ''
    table = ''

    if form.validate_on_submit():
        file = form.file.data
        sheetName = secure_filename(file.filename)

        if form.new_sheet_import.data:

            try:
                df = pandas.read_excel(file,
                                       names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability',
                                              'Data Sanitization Field', 'Next Process Field', 'HDD MFG',
                                              'HDD Serial #',
                                              'Manufacturer', 'Model', 'Serial Number', 'Asset', 'Customer Name',
                                              'Sales Rep', 'New/Used',
                                              'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)',
                                              'Media', 'COA',
                                              'Form Factor', 'Tech Initials', 'Date', 'Cosmetic Condition / Grade',
                                              'Functional Condition / Grade', 'AC Adapter Included', 'Screen Size',
                                              'Test Result Codes', 'Battery Load Test',
                                              'Original Design Battery Capacity',
                                              'Battery Capacity @ Time of Test', 'Percent of Original Capacity',
                                              'Battery Pass/Fail',
                                              'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)',
                                              'Disposition', 'Power Supply', 'Motherboard/CPU', 'Hard Drive',
                                              'Memory', 'USB Ports', 'Peripheral Port', 'Card Reader',
                                              'Optical Drive', 'Screen', 'Screen Hinge', 'Trackpad', 'Keyboard',
                                              'Screen/Backlights'], index_col=None)

                newSheetRow = imported_sheets(sheetName=sheetName, importTime=datetime.now(), user_id=current_user.id)
                db.session.add(newSheetRow)
                db.session.commit()

                sheet = imported_sheets.query.filter_by(sheetName=sheetName).first()
                sheet_name_id = sheet.sheetID

                df.loc[:, ['sheet_id']] = sheet_name_id

                frame = df.to_sql("Production", sqlEngine, if_exists='append', index=False)

            except ValueError as vx:
                sheet_name_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
                db.session.delete(sheet_name_query)
                db.session.commit()
                shape = vx
            except Exception as ex:
                sheet_name_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
                db.session.delete(sheet_name_query)
                db.session.commit()
                shape = ex
            else:
                shape = f'{sheetName} has imported successfully with {frame} rows'
                table = df.replace(np.nan, 'N/A').to_html(classes='table table-light')

    return render_template('import_pandas.html', form=form, shape=shape, table=table, user=current_user)


# -----------------------------------------------------------------------------------------------


@views.route('/validation_entry', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Validation')
def validation_addition():
    """
    For adding a record to the drive validation log.
    Requires make, model, serialNo.
    Date and Sanitization checkbox are required for form to submit.
    """
    form = ValidationEntryForm()

    if form.validate_on_submit():
        # form = request.form
        disk_info_field = form.disk_info.data
        serial_field = form.serial.data
        sanitization_field = form.sanitization.data
        date_field = form.valid_date.data
        initials_field = form.initials.data

        # print(disk_info_field, serial_field, sanitization_field, date_field, initials_field)

        # This can be replaced by the DataRequired() validator in the form itself, but hasn't been yet.
        # if not [x for x in (disk_info_field, serial_field, initials_field) if x is None]:
        try:
            record = VALIDATION(DiskInfo=disk_info_field, DiskSerial=serial_field, Sanitized=int(sanitization_field),
                                Date=date_field, Verification=initials_field)
            # print(record)
            db.session.add(record)
            db.session.commit()
            # print('\n\nUploaded!\n\n')
            flash('Validation entry added!', category='success')
            # db.get_engine(app, 'hdd_db').execute(record)

        except AttributeError:
            db.session.rollback()
            flash('Something is wrong with your data!', category='error')
            # print('\n\nSomething is wrong with your data!\n\n')

        except exc.IntegrityError:
            db.session.rollback()
            flash('Error! This could be duplicate information!', category='error')
            # print('\n\nError! This could be duplicate information!\n\n')

    return render_template('validate_new.html', form=form, user=current_user)


# ------------------------------------------------------------------------------------------------------


@views.route('/validation_mass_import', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Validation')
def validation_import():
    """
        For uploading validations to the new Validation log for all departments.
        Needs to be moved to views.py and added to the validation navigation options
    """

    form = ImportForm()

    shape = ''
    table = ''

    if form.validate_on_submit():
        try:
            file = form.file.data
            columnNames = MasterVerificationLog.query.filter(MasterVerificationLog.autoID < 20).statement.columns.keys()

            # Need to remove autoID from the column names bc it is not included in the spreadsheet.
            # SQL will give these a value automatically when uploaded.
            columnNames.remove('autoID')

            # 'file' refers to the name of the input field from the HTML document
            df = pandas.read_excel(file,
                                   names=columnNames,
                                   index_col=None)

            frame = df.to_sql("MasterVerificationLog", validEngine, if_exists='append', index=False)

        except ValueError as vx:
            shape = vx
        except Exception as ex:
            shape = ex
        else:
            shape = f'Imported successfully with {frame} rows'
            table = df.replace({np.nan: 'N/A', 1: 'Pass', 0: 'Fail'}).to_html(classes='table table-light')

    return render_template('import_pandas.html', form=form, shape=shape, table=table, user=current_user)


# -----------------------------------------------------------------------------------------------------


@views.route('/servers', methods=['GET'])
@login_required
@hf.user_permissions('Admin')
def servers():
    hosts = []
    most_recent_results = []

    get_hosts = BATCHES.query.group_by(BATCHES.Host)

    for result in get_hosts:
        hosts.append(result.Host)

    for host in hosts:
        try:
            recent = BATCHES.query.filter_by(Host=host).order_by(desc(BATCHES.Finished)).first()
            finished = recent.Finished
            # Calculate the time difference between the current time and the server's finished time
            time_difference = datetime.now() - finished
            is_expired = time_difference >= timedelta(hours=24)
            most_recent_results.append({
                'host': host,
                'finished': recent.Finished.strftime("%m-%d-%Y %H:%M:%S"),
                'batch': recent.Batch,
                'is_expired': is_expired  # Add a flag to indicate if the server is expired
            })
        except Exception as e:
            print(host, str(e))

    print(most_recent_results)

    return render_template('servers.html', results=most_recent_results, user=current_user)


@views.route('/servers/<host>', methods=['GET'])
@login_required
@hf.user_permissions('Admin')
def server_details(host):
    try:
        recent = BATCHES.query.filter_by(Host=host).order_by(desc(BATCHES.Finished)).first()
        batch_info = {
            'host': host,
            'finished': recent.Finished.strftime("%m/%d/%Y %H:%M:%S"),
            'batch': recent.Batch
        }
        # You can pass the batch_info dictionary to the template and render it accordingly
        return render_template('server_details.html', batch_info=batch_info, user=current_user)
    except Exception as e:
        print(host, str(e))
        # Handle the case where the recent batch information is not found for the specified server
        # For example, you can display an error message or redirect the user back to the servers page
        return render_template('servers.html', error_message='Recent batch information not found.', user=current_user)


# @views.route('/servers/<finished>', methods=['GET'])
# @login_required
# @hf.user_permissions('Admin')
# def server_details(host):
#     try:
#         recent = BATCHES.query.filter_by(Finished=finished).order_by(desc(BATCHES.Finished)).first()
#         batch_info = {
#             'host': host,
#             'finished': recent.Finished.strftime("%m/%d/%Y %H:%M:%S"),
#             'batch': recent.Batch
#         }
#         # You can pass the batch_info dictionary to the template and render it accordingly
#         return render_template('server_details.html', batch_info=batch_info, user=current_user)
#     except Exception as e:
#         print(host, str(e))
#         # Handle the case where the recent batch information is not found for the specified server
#         # For example, you can display an error message or redirect the user back to the servers page
#         return render_template('servers.html', error_message='Recent batch information not found.',
#                                user=current_user)
#
# @views.route('/servers/<batch>', methods=['GET'])
# @login_required
# @hf.user_permissions('Admin')
# def server_details(host):
#     try:
#         recent = BATCHES.query.filter_by(Batch=batch).order_by(desc(BATCHES.Finished)).first()
#         batch_info = {
#             'host': host,
#             'finished': recent.Finished.strftime("%m/%d/%Y %H:%M:%S"),
#             'batch': recent.Batch
#         }
#         # You can pass the batch_info dictionary to the template and render it accordingly
#         return render_template('server_details.html', batch_info=batch_info, user=current_user)
#     except Exception as e:
#         print(host, str(e))
#         # Handle the case where the recent batch information is not found for the specified server
#         # For example, you can display an error message or redirect the user back to the servers page
#         return render_template('servers.html', error_message='Recent batch information not found.',
#                                user=current_user)


@views.route('/qr-search', methods=["GET", "POST"])
def qr_test():
    form = CustomerSearchForm()
    results = None

    if form.validate_on_submit():
        bol_number = form.bol_number.data
        customer_name = form.customer_name.data
        sales_rep = form.sales_rep.data

        if customer_name:
            results = Customers.query.filter(Customers.customer_name.like(f"%{customer_name}%")).all()

            # for result in results:
            #     print(result.customer_name)

    return render_template('qr_search.html', form=form, results=results, user=current_user)


@views.route('/generate_qr/<string:customer_name>')
def generate_qr_code(customer_name):
    return qrcode(customer_name, mode="raw")


def aiken_query(form):
    AikenSession = sessionmaker(bind=db.get_engine('aiken_db'))
    session = AikenSession()

    filters = []

    if form.start_date.data and form.end_date.data:
        start_date = datetime.combine(form.start_date.data, datetime.min.time())
        end_date = datetime.combine(form.end_date.data, datetime.max.time())
        filters.append(Units.Audited.between(start_date, end_date))
    elif form.start_date.data:
        start_date = datetime.combine(form.start_date.data, datetime.min.time())
        filters.append(Units.Audited >= start_date)
    elif form.end_date.data:
        end_date = datetime.combine(form.end_date.data, datetime.max.time())
        filters.append(Units.Audited <= end_date)
    if form.active_lots.data:
        filters.append(Lots.Status == 0)

    query = (
        db.session.query(
            Units.User,
            func.date(Units.Audited).label('AuditedDate'),
            func.count(Units.UnitID).label('UnitsCount')
        )
        .join(Lots, Units.LotID == Lots.LotID)
        .filter(and_(*filters))
        .group_by(Units.User, func.date(Units.Audited))
        .order_by(func.date(Units.Audited).desc(), Units.User)
    )

    return query


@views.route('/aiken-production', methods=['GET', 'POST'])
@login_required
def aiken_daily_production():
    """
    Allows a user to check production values for a range of dates, as well as limiting
    the search to currently active lots.
    :return: Either a graph or a table. Can also download the table.
    """

    form = AikenProductionForm()
    page = request.args.get('page', 1, type=int)

    if form.validate_on_submit():
        query = aiken_query(form)

        if form.graph.data:
            img_stream = production_graph(query.all())
            return Response(img_stream.getvalue(), content_type='image/png')

        if form.table.data:
            results = query.paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)

            return render_template('aiken_daily_production.html', query=results.items, form=form, user=current_user,
                                   pagination=results)

        if form.download.data:
            results = query.all()

            df = pandas.DataFrame(results, columns=['User', 'Audited Date', 'Units Count'])

            # print(df.head())

            output = BytesIO()
            with pandas.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Aiken Production', index=False)

            output.seek(0)
            return send_file(output, download_name=f"Aiken Production { datetime.today().strftime('%Y-%m-%d') }.xlsx",
                             as_attachment=True)

    return render_template('aiken_daily_production.html', form=form, user=current_user)


def aiken_bol_query(form):
    AikenSession = sessionmaker(bind=db.get_engine('aiken_db'))
    session = AikenSession()

    search_string = form.search.data.strip()
    # print(search_string)

    # Set the @search_string variable needed by the p2() function in MySQL
    session.execute(text('SET @search_string = :search'), {'search': search_string})
    session.commit()

    # Test to make sure the @search_string mysql variable is being set.
    # test_result = session.execute(text('SELECT @search_string')).fetchone()
    # print(f"@search_string is set to: {test_result[0]}")

    # Test that the p2() mysql function is functional and returning the @search_string variable.
    # p2_result = session.execute(text('SELECT p2()')).fetchone()
    # print(f'p2() returned: {p2_result[0]}')

    # Start with the view filtered by @search_string and optionally narrow by date range
    query = session.query(UnitsDevicesSearch)

    # Apply date range filters on the Audited timestamp if provided
    if getattr(form, 'start_date', None) and form.start_date.data:
        s_dt = datetime.combine(form.start_date.data, datetime.min.time())
        query = query.filter(UnitsDevicesSearch.Audited >= s_dt)
    if getattr(form, 'end_date', None) and form.end_date.data:
        # make end boundary exclusive by advancing to the next day at midnight
        e_dt_next = datetime.combine(form.end_date.data + timedelta(days=1), datetime.min.time())
        query = query.filter(UnitsDevicesSearch.Audited < e_dt_next)

    results = query.all()

    session.close()

    return results


@views.route('/aiken-unit-search', methods=['GET', 'POST'])
@login_required
def aiken_unit_search():
    """
    For searching and returning Units results for a full report from Aiken.
    The goal is to return a table of units whose Devices match a provided criteria.
    :return: Blank form or table with provided data
    """
    form = AikenDeviceSearchForm()

    if form.validate_on_submit():

        results = aiken_bol_query(form)

        if form.download.data:

            return download_results(results)

        return render_template('aiken_device_search.html', form=form, results=results, user=current_user)

    return render_template('aiken_device_search.html', form=form, user=current_user)


@views.route('/new-server-addon', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Servers')
def new_server_addon():
    """
    Add a new server add on card to the table.
    Use the Server_AddOn form and model.
    """
    form = Server_AddOn_Form()

    # If the form is validated, which currently takes any string input, add it to the table.
    if form.validate_on_submit():
        entry = Server_AddOns(PID=form.pid.data, make=form.make.data, model=form.model.data)
        db.session.add(entry)
        db.session.commit()
        # Redirect to a fresh version of the page. This helps prevent duplicate entries.
        # Not sure if this line is necessary, as the next line will essentially do the same thing.
        return redirect(url_for('views.new_server_addon'))

    # Return the HTML template to use for this view.
    return render_template('skeleton_server_addons.html', form=form, user=current_user)


@views.route('/search-server-addon', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Servers')
def search_server_addon():
    """
    Search for AddOn results from the Server_AddOn table.
    Allow user to add options from search to 'results', then
    use results to generate a QR code the user can print.
    """
    form = Server_AddOn_Form()
    results = None

    if form.validate_on_submit():
        # if session 'selected_items' exists, print the contents.
        # if 'selected_items' in session:
        #     print('Validated Session:', session['selected_items'])
        # else:
        #     print('No data in session variable')

        # If the clear button is pressed, removed selected_items from the session.
        if form.clear.data:
            if 'selected_items' in session:
                session.pop('selected_items')
            return redirect(url_for('views.search_server_addon'))

        # If the generate button is pressed, generate QR codes from the session variable.
        if form.generate.data:
            return redirect(url_for('views.generate_qr_addon'))

        # Get a reference to all values passed from the form.
        pid = form.pid.data
        make = form.make.data
        model = form.model.data

        # Create an empty query for the Server_AddOns model
        query = Server_AddOns.query
        # Create an empty filters list to be populated
        filters = []
        # If data existed in the PID field, add it to the filters
        if pid:
            filters.append(Server_AddOns.PID.like(f'%{pid}%'))
        # If data existed in the make field, add it to the filters
        if make:
            filters.append(Server_AddOns.make.like(f'%{make}%'))
        # If data existed in the model field, add it to the filters
        if model:
            filters.append(Server_AddOns.model.like(f'%{model}%'))

        # Filter the Server_Addons table by the filters that have been added, if any
        if filters:
            query = query.filter(and_(*filters))
        # Get all results matching the filters
        results = query.all()
        # Print for debugging the results
        # for result in results:
        #     print(result.autoID)

    return render_template('skeleton_server_addons_search.html', form=form, results=results, user=current_user)


@views.route('/generate-qr-addon', methods=['GET'])
@login_required
@hf.user_permissions('Servers')
def generate_qr_addon():
    """
    Takes data from the session and generates necessary QR codes from it.
    """
    session_key = 'selected_items'  # Set the term for session key
    # If the session does not contain the session key, return.
    if session_key not in session:
        print('No session key in session!')
        return redirect(url_for('views.search_server_addon'))

    # Save the session string to a local variable, then clear the session.
    session_data = session[session_key]
    session.pop(session_key, None)

    # For debugging purposes. Not necessary.
    print('QR Data:', session_data)

    # Get a list of strings that match the necessary parameters for Aiken (99 Characters max)
    string_list = character_count_for_qr(session_data)

    print('String_list:', string_list)

    # This return is temporary until I put together an HTML framework for it.
    return render_template('skeleton_generate_server_qr.html', string_list=string_list, user=current_user)


@views.route('/add-to-session', methods=['POST'])
def add_to_session():
    """
    Handle AJAX requests from server addons.
    """
    print('Called add-to-session')
    data = request.json  # Get JSON data from the request object
    print(f'Received Data: {data}')
    quantity = data['quantity']  # Store quantity data
    pid = data['pid']  # Store PID data
    make = data['make']  # Store Make data
    model = data['model']  # Store Model data

    # Set the name of the session object.
    session_key = 'selected_items'
    # Check if the session object already exists.
    if session_key not in session:
        session[session_key] = ''

    # Add the string to the session.
    session[session_key] += f'({quantity}) {pid} {make} {model}, '

    # Add the selected result to the database as a search.
    entry = Searches_Addons(user=current_user.email, date=datetime.now(), pid=pid, make=make, model=model)
    db.session.add(entry)
    db.session.commit()

    # Return a message to the user.
    return jsonify({"message": session[session_key]})


@views.route('/network-price-import', methods=['GET', 'POST'])
def network_price_import():
    """
    View function to import Price Data for Network Objects as provided by Brett
    """
    # Create an instance of the import form
    form = ImportForm()
    message = ''

    if form.validate_on_submit():  # After the form has been submitted
        try:
            # Get a reference to the uploaded file
            file = form.file.data

            # Get a list of the column names from the table itself.
            # noinspection PyTypeChecker
            column_names = get_column_names(Network_Price_Data)
            column_names.remove('autoID')  # Remove autoID from the column list
            column_names.remove('date')  # Date removed temporarily so file can be loaded into pandas

            # Convert the file data into a pandas dataframe.
            df = pandas.read_excel(file,
                                   names=column_names,
                                   index_col=None)
            df = df.fillna({
                'mfg': '',
                'model': '',
                'serial': '',
                'addons': '',
                'psu_info': '',
                'fans': '',
                'test_result_codes': '',
            })
            # Replace NaN values in 'Fans' column with False
            df['price'] = df['price'].fillna(False)
            # Replace NaN values in 'Fans' column with False
            df['addons'] = df['addons'].fillna(False)
            # Replace NaN values in 'Fans' column with False
            df['year'] = df['year'].fillna(False)
            # Replace NaN values in 'Winning Bid' column with False
            df['winning_bid'] = df['winning_bid'].fillna(False)
            # convert the dataframe to a dictionary with the keyword 'records'
            records = df.to_dict('records')

            # Iterate over each record and insert it using SQLAlchemy
            for record in records:
                # Set 'Date' explicitly
                record['date'] = date.today()
                # Create a new SQLAlchemy object with the record information
                new_record = Network_Price_Data(**record)
                # add the new record to the database
                db.session.add(new_record)
            db.session.commit()
        # Handle exceptions, and rollback database commit
        except Exception as e:
            db.session.rollback()
            message = e
            print(e)

    return render_template('skeleton_network_price_import.html', form=form, message=message, user=current_user)


@views.route('/network-price-search', methods=['GET', 'POST'])
def network_price_search():
    # Create a new instance of the search form.
    form = NetworkPricingSearchForm()

    # Get the page number from pagination widget
    page = request.args.get('page', 1, type=int)

    if form.clear.data:
        session.clear()
        return redirect(url_for(request.endpoint))

    results = None

    if form.validate_on_submit():
        session['manufacturer'] = form.mfg.data
        session['model'] = form.model.data
        session['addons'] = form.addons.data
        session['min_price'] = form.min_price.data
        session['max_price'] = form.max_price.data
        session['test_codes'] = form.test_codes.data
        session['start_date'] = form.start_date.data
        session['end_date'] = form.end_date.data
        session['winning_bid'] = form.winning_bid.data

    manufacturer = session.get('manufacturer')
    model = session.get('model')
    addons = session.get('addons')
    min_price = session.get('min_price')
    max_price = session.get('max_price')
    test_codes = session.get('test_codes')
    start_date = session.get('start_date')
    end_date = session.get('end_date')
    winning_bid = session.get('winning_bid')

    query = Network_Price_Data.query
    filters = []

    if form.mfg.data:  # Use MFG Search
        like_string = "%{}%".format(form.mfg.data)  # Create a search string
        filters.append(Network_Price_Data.mfg.like(like_string))
    if form.model.data:  # Use Model Search
        like_string = "%{}%".format(form.model.data)  # Create a search string
        filters.append(Network_Price_Data.model.like(like_string))
    if form.addons.data:  # Use Add-On Search
        like_string = "%{}%".format(form.addons.data)  # Create a search string
        filters.append(Network_Price_Data.addons.like(like_string))
    if form.min_price.data and form.max_price.data:  # Handle both min and max prices entered
        filters.append(Network_Price_Data.price.between(form.min_price.data, form.max_price.data))
    elif form.min_price.data:  # Handle just a minimum price
        filters.append(Network_Price_Data.price >= form.min_price.data)
    elif form.max_price.data:  # Handle just a maximum price
        filters.append(Network_Price_Data.price <= form.max_price.data)
    if form.test_codes.data:  # Handle a test code string
        like_string = "%{}%".format(form.test_codes.data)  # Create a search string
        filters.append(Network_Price_Data.test_codes.like(like_string))
    if form.start_date.data and form.end_date.data:  # Handle both start and end dates
        # Add a time to the dates so that it starts at the beginning of the day? May not be necessary
        start_date = datetime.combine(form.start_date.data, datetime.min.time())
        end_date = datetime.combine(form.end_date.data, datetime.max.time())
        filters.append(Network_Price_Data.date.between(start_date, end_date))
    elif form.start_date.data:  # Handle just a start date
        start_date = datetime.combine(form.start_date.data, datetime.min.time())
        filters.append(Network_Price_Data.date >= start_date)
    elif form.end_date.data:  # Handle just an end date
        end_date = datetime.combine(form.end_date.data, datetime.max.time())
        filters.append(Network_Price_Data.date <= end_date)
    if form.winning_bid.data:  # Check if the user only wants winning bids
        filters.append(Network_Price_Data.winning_bid == form.winning_bid.data)

    if filters:
        query = query.filter(and_(*filters))

    results = query.paginate(page=page, per_page=ROWS_PER_PAGE, error_out=False)

    if not form.validate_on_submit() and not (manufacturer or model or addons or min_price or max_price or test_codes or start_date or end_date or winning_bid):
        return render_template('skeleton_network_price_search.html', form=form, user=current_user)

    return render_template('skeleton_network_price_search.html', form=form, pagination=results, user=current_user,
                           columns=get_column_names(Network_Price_Data))


# === End of Views ===

# === Functions ===


def production_graph(query):
    """
    Creates a graph based on a passed query for Aiken and stores it in memory.
    :return: A BytesIO object called img_stream for display in the browser.
    """

    df = pandas.DataFrame(query, columns=['User', 'AuditedDate', 'UnitsCount'])
    agg_data = df.groupby('User').sum()['UnitsCount'].reset_index()

    plt.figure(figsize=(15, 6))
    ax = sns.barplot(data=agg_data, x='User', y='UnitsCount')
    plt.title('Total Units Count By User')

    for index, value in enumerate(agg_data['UnitsCount']):
        ax.text(index, value + 0.5, str(value), ha='center', va='center')

    plt.tight_layout()

    img_stream = BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)

    return img_stream


def download_results(results):
    """
    Used for creating an Excel file with the results of a SQLAlchemy query, as used in 'views.aiken_bol_query()'.
    :return: send_file Excel file of the passed results.
    """

    # Extract column names from the model in the order they are described in.
    column_order = [column.name for column in UnitsDevicesSearch.__table__.columns]

    # Convert the SQLAlchemy objects to dictionaries
    results_as_dicts = [r.__dict__ for r in results]

    # Exclude the SQLAlchemy state instance from the dictionaries
    results_as_dicts = [{key: value for key, value in r.items() if key != '_sa_instance_state'} for r in results_as_dicts]

    df = pandas.DataFrame(results_as_dicts)
    # Reorder the DataFrame to match the columns
    df = df[column_order]

    output = BytesIO()
    with pandas.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Aiken BOL Report', index=False)

    output.seek(0)
    return send_file(output, download_name=f"Aiken BOL Report {datetime.today().strftime('%Y-%m-%d')}.xlsx", as_attachment=True)


def character_count_for_qr(session_string):
    """
    Take the string of add-ons, count the number of characters,
    and split it into the necessary strings for QR codes.
    :return: list of strings
    """
    # Split the string into a list of devices
    session_arr = session_string.split(', ')
    print('Session_arr:', session_arr)

    character_count = 0  # Set the initial character count to 0
    qr_code_strings = []  # Create an empty list used to store strings for QR codes
    current_string = None  # Keep a record of the ongoing string

    for string in session_arr:

        if (len(string) + character_count + 2) >= 100:
            qr_code_strings.append(current_string)
            current_string = None
            character_count = 0

        if len(string) == 0:
            break
        # Add the current string length to the character count,
        # With a padding for the ', ' characters between entries.
        elif (len(string) + character_count + 2) < 100:
            current_string = current_string + ', ' + string if current_string else string
            character_count += len(string) + 2
            print('Current String:', len(current_string), current_string)

    if len(current_string) > 0:
        qr_code_strings.append(current_string)

    print('qr_code_strings:', qr_code_strings)
    return qr_code_strings


def get_column_names(model):
    """
    :param model: The model to get column names for
    :return: list of column names from the model
    """
    # return [column.key for column in model.__table__.columns]
    return [column.key for column in inspect(model).mapper.column_attrs]

# === End of Views ===

# === Functions ===
