from flask import Flask, Blueprint, render_template, flash, request, jsonify, send_file, session, url_for
from flask_login import login_required, current_user
from sqlalchemy import exc
# from sqlalchemy import create_engine
from .models import Note, Production, imported_sheets, DISKS, VALIDATION, MasterVerificationLog
from . import db, sqlEngine, validEngine, app
import json
import flask_excel as excel
import pandas as pandas
# import pymysql as pms
from .forms import ProductionSearchForm, TemplateDownloadForm, ValidationEntryForm, ImportForm
from datetime import datetime
import numpy as np
import os
from datetime import date

views = Blueprint('views', __name__)


# --------------------------------------------------------------------------------------


@views.route('/site-map', methods=['GET', 'POST'])
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
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    
    return jsonify({})


# For viewing the table layout required for CycleLutions. No limit function
@views.route('/cyclelutions_upload')
def cycleLutionsImport():
    imp = db.session.execute('SELECT `Order Number` AS OrderNo, `Product Name` AS ProductName, 1 AS Qty, "Units" AS QtyBase, 0 AS Weight, "lbs" AS WeightBase, "N" AS RTS, "N" AS TDM, `Serial Number` AS SerialNo, NULL AS BusID, `Sale Category` AS "Condition", `Manufacturer` AS Manufacturer, `Model` AS Model, NULL AS Color, `Screen Size` AS ScreenSize, `Physical Condition/ Grade` AS Grade, `Media` AS Media, NULL AS ReceivingNotes, `Year Manufactured` AS YearOfMFG, `R2 Applicability` AS R2Applicability, `Data Sanitization Field` AS DataSanitizationField, `Next Process Field` AS NextProcessField, `DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)` AS DataWipe, `New/Used` AS newOrUsed, `Form Factor` AS FormFactor, `Battery Load Test` AS BatteryLoadTest, `Battery Pass/Fail` AS BatteryStatus, `AC Adapter Included` AS ACAdapterIncluded, NULL AS DDL1, NULL AS DDL2, NULL AS DDL3, NULL AS DDL4, NULL AS DDL5, NULL AS DDL6, `Processor` AS Processor, `Speed` AS Speed, `HDD (GB)` AS HDDSize, `RAM (GB)` AS RAM, `COA` AS coa, `Tech Initials` AS TechInitials, `Asset` AS AssetTag, `HDD MFG` AS HddMFG, `HDD Serial #` AS HddSerial, `Unit #` AS UnitNo, `Date` AS "Date", `Percent of Original Capacity` AS PercentOrgCapacity, `Original Design Battery Capacity` AS OrgDesignCapacity, `Battery Capacity @ Time of Test` AS CurrentCapacity, `Test Result Codes` AS TestResultCodes FROM Production')
    return render_template('cyclelutions_upload.html', user=current_user, imp=imp)


# Testing. Pulls tables from Category and Post
# @views.route("/handson_view", methods=['GET'])
# def handson_table():
#    return excel.make_response_from_tables(
#        db.session, [Category, Post], 'handsontable.html')


# Pulls tables from Production for handsontable
@views.route("/handson", methods=['GET'])
def cycle_handson():
    return excel.make_response_from_tables(
        db.session, [Production], 'handsontable.html')


# for exporting in CycleLutions format
@views.route('/custom_export', methods=['GET'])
def docustomexport():
    query_sets = db.session.execute('SELECT `Order Number` AS OrderNo, `Product Name` AS ProductName, 1 AS Qty, "Units" AS QtyBase, 0 AS Weight, "lbs" AS WeightBase, "N" AS RTS, "N" AS TDM, `Serial Number` AS SerialNo, NULL AS BusID, `Sale Category` AS "Condition", `Manufacturer` AS Manufacturer, `Model` AS Model, NULL AS Color, `Screen Size` AS ScreenSize, `Physical Condition/ Grade` AS Grade, `Media` AS Media, NULL AS ReceivingNotes, `Year Manufactured` AS YearOfMFG, `R2 Applicability` AS R2Applicability, `Data Sanitization Field` AS DataSanitizationField, `Next Process Field` AS NextProcessField, `DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)` AS DataWipe, `New/Used` AS newOrUsed, `Form Factor` AS FormFactor, `Battery Load Test` AS BatteryLoadTest, `Battery Pass/Fail` AS BatteryStatus, `AC Adapter Included` AS ACAdapterIncluded, NULL AS DDL1, NULL AS DDL2, NULL AS DDL3, NULL AS DDL4, NULL AS DDL5, NULL AS DDL6, `Processor` AS Processor, `Speed` AS Speed, `HDD (GB)` AS HDDSize, `RAM (GB)` AS RAM, `COA` AS coa, `Tech Initials` AS TechInitials, `Asset` AS AssetTag, `HDD MFG` AS HddMFG, `HDD Serial #` AS HddSerial, `Unit #` AS UnitNo, `Date` AS "Date", `Percent of Original Capacity` AS PercentOrgCapacity, `Original Design Battery Capacity` AS OrgDesignCapacity, `Battery Capacity @ Time of Test` AS CurrentCapacity, `Test Result Codes` AS TestResultCodes FROM Production')
    column_names = ['OrderNo', 'ProductName', 'Qty', 'QtyBase', 'Weight', 'WeightBase', 'RTS', 'TDM', 'SerialNo', 'BusID', 'Condition', 'Manufacturer', 'Model', 'Color', 'ScreenSize', 'Grade', 'Media', 'ReceivingNotes', 'YearOfMFG', 'R2Applicability', 'DataSanitizationField', 'NextProcessField', 'DataWipe', 'newOrUsed', 'FormFactor', 'BatteryLoadTest', 'BatteryStatus', 'ACAdapterIncluded', 'DDL1', 'DDL2', 'DDL3', 'DDL4', 'DDL5', 'DDL6', 'Processor', 'Speed', 'HDDSize', 'RAM', 'coa', 'TechInitials', 'AssetTag', 'HddMFG', 'HddSerial', 'UnitNo', 'Date', 'PercentOrgCapacity', 'OrgDesignCapacity', 'CurrentCapacity', 'TestResultCodes']
    return excel.make_response_from_query_sets(query_sets, column_names, "csv")


# Exports marketing for Brett.
# N/A For HDD information.
@views.route('/marketing_export', methods=['GET'])
def doMarketingExport():
    query_sets = db.session.execute('SELECT `Unit #` AS "Unit #",`Product Name` AS "Product Name", "NA" AS "HDD MFG", "NA" AS "HDD Serial #", `Manufacturer` AS "Manufacturer", `Model` AS "Model", `Serial Number` AS "Serial #", `Asset` AS "Asset", `Year Manufactured` AS "Year Manufactured", `Processor` AS Processor, `Speed` AS Speed, `RAM (GB)` AS RAM, `Media` AS Media, `COA` AS COA, `Form Factor` AS "Form Factor", "N/A" AS "HDD (GB)", `Test Result Codes` AS "TEST RESULT CODES (SEE TRANSLATIONS)", `Sale Category` AS "Sale Category" FROM Production')
    column_names = ["Unit #", 'Product Name', "HDD MFG", "HDD Serial #", 'Manufacturer', 'Model', 'Serial #', "Asset", 'Year Manufactured', 'Processor', 'Speed', 'RAM', 'Media', 'COA', 'Form Factor', 'HDD (GB)', "TEST RESULT CODES (SEE TRANSLATIONS)", 'Sale Category']
    return excel.make_response_from_query_sets(query_sets, column_names, "csv")


# # For adding sheet id to Production table, and removing sheetName if import fails
# @views.route('/pandas_import', methods=['GET', 'POST'])
# def safeimport():
#
#     shape = ''
#     table = ''
#
#     if request.method == 'POST':
#
#         dbConnection = sqlEngine.connect()
#
#         sheetName = request.files['file'].filename
#
#         df = pandas.read_excel(request.files.get('file'), names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability', 'Data Sanitization Field', 'Next Process Field', 'HDD MFG', 'HDD Serial #', 'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used', 'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)', 'Media', 'COA', 'Form Factor', 'Tech Initials', 'Date', 'Cosmetic Condition / Grade', 'Functional Condition / Grade', 'AC Adapter Included', 'Screen Size', 'Test Result Codes', 'Battery Load Test', 'Original Design Battery Capacity', 'Battery Capacity @ Time of Test', 'Percent of Original Capacity', 'Battery Pass/Fail', 'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)', 'Sale Category'], index_col=None)
#
#         # namecheck = imported_sheets.query.filter_by(sheetName=sheetName).first()
#         # if namecheck:
#         #    shape = 'This sheet has already been imported!'
#         # else:
#         # add filename of imported file to imported_sheets table
#         newSheetRow = imported_sheets(sheetName=sheetName, importTime=datetime.now(), user_id=current_user.id)
#         db.session.add(newSheetRow)
#
#         db.session.commit()
#
#         sheet = imported_sheets.query.filter_by(sheetName=sheetName).first()
#         sheetName_id = sheet.sheetID
#
#         # This line adds a column to the end of the dataframe and assigns it a value.
#         df.loc[:,['sheet_id']] = sheetName_id
#         # print('Imported Sheet #: ' + str(sheetName_id))
#
#         try:
#             frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)
#         except ValueError as vx:
#             sheetName_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
#             db.session.delete(sheetName_query)
#             db.session.commit()
#             # print('Tried vx')
#             shape = vx
#
#             # undo the session changes (drop the sheetName)
#             # ##This doesnt work bc it has already been committed
#             # db.session.rollback()
#         except Exception as ex:
#             sheetName_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
#
#             db.session.delete(sheetName_query)
#             db.session.commit()
#             shape = ex
#             # undo the session changes (drop the sheetName)
#             # db.session.rollback()
#             # print(ex)
#         # except sqlalchemy.exc.IntegrityError as integer:
#             # shape = integer
#             # db.session.delete(sheetName)
#             # db.session.commit()
#             # print('Tried integr')
#         # except sqlalchemy.orm.exc.UnmappedInstanceError as unmapinst:
#             # shape = unmapinst
#             # db.session.delete(sheetName)
#             # db.session.commit()
#             # print('Tried unmapinst')
#         # except exc.IntegrityError as interr:
#         #    print('EXCEPTION EXCEPTION EXCEPTION EXCEPTION EXCEPTION EXCEPTION')
#         #    shape = 'This spreadsheet has already been uploaded! (sql)'
#         # except pms.err.IntegrityError as interr:
#         #    shape = 'This spreadsheet has already been uploaded! (pms)'
#         else:
#             shape = '{} has imported successfully with {} rows'.format(sheetName, frame)
#             #table = df.to_html(classes='table')
#             table = df.replace(np.nan,'N/A').to_html(classes='table table-dark')
#         finally:
#             dbConnection.close()
#
#
#
#         #return render_template('import_pandas.html', shape = df.shape, user=current_user)
#         #table is a variable in the sheet. Marked with "|safe" so that it renders as html, not as text.
#         #return render_template('pandas_table.html', table=table, user=current_user)
#     return render_template('import_pandas.html', shape=shape, table=table, user=current_user)

# -----------------------------------------------------------------------------------------------
# For adding sheet id to Production table, and removing sheetName if import fails
@views.route('/pandas_import', methods=['GET', 'POST'])
@login_required
def safeimport():

    form = ImportForm()

    frame = None

    shape = ''
    table = ''

    if request.method == 'POST':

        sheetName = request.files['file'].filename

        with sqlEngine.connect() as dbConnection:
            if form.new_sheet_import.data:

                try:
                    # df = pandas.read_excel(request.files.get('file'),
                    #            names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability',
                    #                   'Data Sanitization Field', 'Next Process Field', 'HDD MFG', 'HDD Serial #',
                    #                   'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used',
                    #                   'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)', 'Media', 'COA',
                    #                   'Form Factor', 'Tech Initials', 'Date', 'Cosmetic Condition / Grade',
                    #                   'Functional Condition / Grade', 'AC Adapter Included', 'Screen Size',
                    #                   'Test Result Codes', 'Battery Load Test', 'Original Design Battery Capacity',
                    #                   'Battery Capacity @ Time of Test', 'Percent of Original Capacity',
                    #                   'Battery Pass/Fail', 'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)',
                    #                   'Sale Category'], index_col=None)

                    df = pandas.read_excel(request.files.get('file'),
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

                    frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)

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

            if form.old_sheet_import.data:
                try:
                    old_column_one = "PHYSICAL CONDITION/ GRADE "
                    old_column_two = "PHYSICAL CONDITION / GRADE "
                    new_cosmetic_column = "Cosmetic Condition / Grade"
                    new_functional_column = "Functional Condition / Grade"
                    physical_index = None

                    df = pandas.read_excel(request.files.get('file'),
                                           names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability',
                                                  'Data Sanitization Field', 'Next Process Field', 'HDD MFG',
                                                  'HDD Serial #',
                                                  'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used',
                                                  'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)',
                                                  'Media', 'COA',
                                                  'Form Factor', 'Tech Initials', 'Date', 'PHYSICAL CONDITION/ GRADE ',
                                                  'AC Adapter Included', 'Screen Size',
                                                  'Test Result Codes', 'Battery Load Test',
                                                  'Original Design Battery Capacity',
                                                  'Battery Capacity @ Time of Test', 'Percent of Original Capacity',
                                                  'Battery Pass/Fail',
                                                  'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)',
                                                  'Sale Category'], index_col=None)
                    newSheetRow = imported_sheets(sheetName=sheetName, importTime=datetime.now(),
                                                  user_id=current_user.id)
                    db.session.add(newSheetRow)
                    db.session.commit()

                    sheet = imported_sheets.query.filter_by(sheetName=sheetName).first()
                    sheet_name_id = sheet.sheetID

                    column_names = list(df.columns.values)

                    if old_column_one in column_names:
                        physical_index = column_names.index(old_column_one)
                        # print(physical_index)
                        df.rename(columns={old_column_one: new_cosmetic_column}, inplace=True)
                        df.insert(physical_index + 1, new_functional_column, value='')
                    elif old_column_two in column_names:
                        physical_index = column_names.index(old_column_two)
                        # print(physical_index)
                        df.rename(columns={old_column_two: new_cosmetic_column}, inplace=True)
                        df.insert(physical_index + 1, new_functional_column, value='')

                    df.loc[:, ['sheet_id']] = sheet_name_id

                    frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)

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


@views.route('/search', methods=['GET', 'POST'])
def search():
    prodForm = ProductionSearchForm()
    if request.method == 'POST':
        form = request.form
        search_term = form['search']
        select_term = form['select']
        #formats string so that it can be passed to filter
        #print(select_term)
        search_format = {select_term: search_term}
        results = Production.query.filter_by(**search_format).all()
        #print(str(results))
        return render_template('search.html', form=prodForm, results=results, user=current_user)
    else:
        return render_template('search.html', form=prodForm, user=current_user)


@views.route('/templates', methods = ['GET', 'POST'])
def download_templates():
    template_form = TemplateDownloadForm()
    if request.method == 'POST':
        app = Flask(__name__)
        form = request.form
        #lt_button = form.laptop_template_download.data
        #dt_button = form.desktop_template_download.data
        #pro_button = form.processing_template_download.data
        #lcd_button = form.lcd_template_download.data

        if template_form.laptop.data:
            file_path = os.path.join(app.root_path, 'excel_templates', '8.9.15-F Equipment Testing and Inventory Workbook – 1.0.xlsx')
            return send_file(file_path)
            # print(str(file_path))
            # print('LT check')
        elif template_form.desktop_template_download.data:
            file_path = os.path.join(app.root_path, 'excel_templates', '8.9.15-F Equipment Testing and Inventory Workbook – 1.0_Desktops.xlsx')
            return send_file(file_path)
        elif template_form.processing_template_download.data:
            file_path = os.path.join(app.root_path, 'excel_templates', '8.9.15-F Equipment Testing and Inventory Workbook – 1.0_Processing.xlsx')
            return send_file(file_path)
        elif template_form.lcd_template_download.data:
            file_path = os.path.join(app.root_path, 'excel_templates', '8.9.15-F Equipment Testing and Inventory Workbook – 1.0_LCDS.xlsx')
            return send_file(file_path)

    return render_template('excel_templates.html', form=template_form, user=current_user)


@views.route('/validation_table', methods=['GET'])
def validation_view():
    records = VALIDATION.query.order_by(VALIDATION.Date.desc())

    return render_template('validation_table.html', form=records, user=current_user)


@views.route('/validation_entry', methods=['GET', 'POST'])
@login_required
def validation_addition():
    """
    For adding a record to the validation log.
    Requires make, model, serialNo.
    Date and Sanitization checkbox are required for form to submit.
    """
    entryform = ValidationEntryForm()

    if request.method == 'POST':
        form = request.form
        disk_info_field = form['disk_info']
        sanitization_field = form['sanitization']
        date_field = form['valid_date']
        serial_field = form['serial']
        initials_field = form['initials']

        # This can be replaced by the DataRequired() validator in the form itself, but hasn't been yet.
        if not [x for x in (disk_info_field, serial_field, initials_field) if x is None]:
            try:
                record = VALIDATION(DiskInfo=disk_info_field, DiskSerial=serial_field, Sanitized=int(sanitization_field),
                                    Date=date_field, Verification=initials_field)
                db.session.add(record)
                db.session.commit()
                print('\n\nUploaded!\n\n')
                flash('Validation entry added!', category='success')
                #db.get_engine(app, 'hdd_db').execute(record)

            except AttributeError:
                # record = VALIDATION.add(Make=make_field, Model=model_field, DiskSerial=serial_field, Date=date.today(), Verification=initials_field)
                # print(record)
                db.session.rollback()
                flash('Something is wrong with your data!', category='error')
                print('\n\nSomething is wrong with your data!\n\n')

            except exc.IntegrityError:
                db.session.rollback()
                flash('Error! This could be duplicate information!', category='error')
                print('\n\nError! This could be duplicate information!\n\n')

        else:
            flash('Something went wrong!', category='error')
            print('\n\nBad IF Statement!\n\n')

    return render_template('validate_new.html', form=entryform, user=current_user)

# ------------------------------------------------------------------------------------------------------

@views.route('validation_mass_import', methods=['GET', 'POST'])
def validation_import():
    """
        For uploading validations to the new Validation log for all departments.
        Needs to be moved to views.py and added to the validation navigation options
    """

    shape = ''
    table = ''

    if request.method == 'POST':

        try:
            with validEngine.connect() as dbConnection:
                columnNames = MasterVerificationLog.query.filter(MasterVerificationLog.autoID < 20).statement.columns.keys()
                print(columnNames)

                # columnNames = columnNames.append('autoID')

                # Need to remove autoID from the column names bc it is not included in the spreadsheet.
                # SQL will give these a value automatically when uploaded.
                columnNames.remove('autoID')

                # 'file' refers to the name of the input field from the HTML document
                df = pandas.read_excel(request.files.get('file'),
                                       names=columnNames,
                                       index_col=None)

                frame = df.to_sql("MasterVerificationLog", dbConnection, if_exists='append', index=False)

        except ValueError as vx:
            shape = vx
        except Exception as ex:
            shape = ex
        else:
            shape = f'Imported successfully with {frame} rows'
            table = df.replace(np.nan, 'N/A').to_html(classes='table table-light')

    return render_template('validation_import.html', shape=shape, table=table, user=current_user)

# -----------------------------------------------------------------------------------------------------

