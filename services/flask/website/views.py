from flask import Flask, Blueprint, render_template, flash, request, jsonify, session, url_for, Response, send_file
from flask_login import login_required, current_user
from sqlalchemy import exc, desc, func, and_
from sqlalchemy.orm import sessionmaker
# from sqlalchemy import create_engine
from .models import Note, imported_sheets, VALIDATION, MasterVerificationLog, BATCHES, Customers, Lots, Units, Units_Devices
from . import db, sqlEngine, validEngine, aikenEngine, app, qrcode
import json
import flask_excel as excel
import pandas as pandas
import seaborn as sns
import matplotlib.pyplot as plt
# import pymysql as pms
from .forms import ValidationEntryForm, ImportForm, CustomerEntryForm, CustomerSearchForm, AikenProductionForm, AikenDeviceSearchForm
from datetime import datetime, timedelta
import numpy as np
import website.helper_functions as hf
from werkzeug.utils import secure_filename
import flask_qrcode
from io import BytesIO


views = Blueprint('views', __name__)


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

    @views.route('/servers/<finished>', methods=['GET'])
    @login_required
    @hf.user_permissions('Admin')
    def server_details(host):
        try:
            recent = BATCHES.query.filter_by(Finished=finished).order_by(desc(BATCHES.Finished)).first()
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
            return render_template('servers.html', error_message='Recent batch information not found.',
                                   user=current_user)

    @views.route('/servers/<batch>', methods=['GET'])
    @login_required
    @hf.user_permissions('Admin')
    def server_details(host):
        try:
            recent = BATCHES.query.filter_by(Batch=batch).order_by(desc(BATCHES.Finished)).first()
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
            return render_template('servers.html', error_message='Recent batch information not found.',
                                   user=current_user)


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

            for result in results:
                print(result.customer_name)

    return render_template('qr_search.html', form=form, results=results, user=current_user)


@views.route('/generate_qr/<string:customer_name>')
def generate_qr_code(customer_name):
    return qrcode(customer_name, mode="raw")


@views.route('/aiken-production', methods=['GET', 'POST'])
@login_required
def aiken_daily_production():
    """
    Allows a user to check production values for a range of dates, as well as limiting
    the search to currently active lots.
    :return: Either a graph or a table. Can also download the table.
    """

    form = AikenProductionForm()

    if form.validate_on_submit():

        query = aiken_query(form)

        if form.graph.data:
            img_stream = production_graph(query.all())
            return Response(img_stream.getvalue(), content_type='image/png')

        if form.table.data:
            return render_template('skeleton_aiken_daily_production.html', query=query.all(), form=form, user=current_user)

        if form.download.data:

            results = query.all()

            df = pandas.DataFrame(results, columns=['User', 'Audited Date', 'Units Count'])

            print(df.head())

            output = BytesIO()
            with pandas.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Aiken Production', index=False)

            output.seek(0)
            return send_file(output, download_name=f"Aiken Production { datetime.today().strftime('%Y-%m-%d') }.xlsx", as_attachment=True)

    return render_template('skeleton_aiken_daily_production.html', form=form, user=current_user)


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

        query = aiken_bol_query(form)

        column_names = get_column_names_from_query(query)
        results = query.all()

        if form.table.data:
            return render_template('skeleton_aiken_device_search.html', query=results, column_names=column_names, form=form, user=current_user)

    return render_template('skeleton_aiken_device_search.html', form=form, user=current_user)


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

    # noinspection PyTypeChecker
    query = (
        session.query(
            Units.User,
            func.date(Units.Audited).label('AuditedDate'),
            func.count(Units.UnitID).label('UnitsCount')
        )
        .join(Lots, Units.LotID == Lots.LotID)
        .filter(and_(*filters))
        .group_by(Units.User, func.date(Units.Audited))
        .order_by(func.date(Units.Audited).desc(), Units.User)
    )

    session.close()

    return query


def aiken_bol_query(form):
    AikenSession = sessionmaker(bind=db.get_engine('aiken_db'))
    session = AikenSession()

    filters = []

    # if form.active_lots.data:
    #     filters.append(Lots.Status == 0)
    # if form.search.data:
    #     if form.select.data == 'BOL':
    #         filters.append(Units_Devices.Category == 'BOL')
    #     if form.select.data == 'CUSTOMER NAME':
    #         filters.append(Units_Devices.Category == 'CUSTOMER NAME')
    #     if form.select.data == 'SALES REP':
    #         filters.append(Units_Devices.Category == 'SALES REP')
    #     filters.append(Units_Devices.Info1.contains(form.search.data))

    query = (
        session.query(
            Lots.LotID.label('LotID'),
            Units,
            Units_Devices.Info1
        )
        .join(Units_Devices, Units.UnitID == Units_Devices.UnitID)
        .join(Lots, Units.LotID == Lots.LotID)
        .filter(and_(*filters))
        .order_by(Units.Audited.desc())
    )

    session.close()

    print("Query", str(query))
    print("Parameters", query.params)

    return query


def get_column_names_from_query(query):
    """
    Takes a query object and pulls the column names from it.
    :return: A list of column names.
    """
    return [column['name'] for column in query.column_descriptions]
