from flask import Flask, Blueprint, render_template, flash, request, jsonify, session, url_for
from flask_login import login_required, current_user
from sqlalchemy import exc, desc
# from sqlalchemy import create_engine
from .models import Note, imported_sheets, VALIDATION, MasterVerificationLog, BATCHES
from . import db, sqlEngine, validEngine, app
import json
import flask_excel as excel
import pandas as pandas
# import pymysql as pms
from .forms import ValidationEntryForm, ImportForm
from datetime import datetime
import numpy as np
import website.helper_functions as hf
from werkzeug.utils import secure_filename


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

@views.route('/servers', methods = ['GET'])
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
            most_recent_results.append([host, recent.Finished.strftime("%m/%d/%Y %H:%M:%S"), recent.Batch])
        except Exception as e:
            print(host, str(e))

    print(most_recent_results)

    return render_template('servers.html', results=most_recent_results, user=current_user)