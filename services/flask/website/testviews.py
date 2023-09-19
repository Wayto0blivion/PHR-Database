from time import strftime
from . import app
from flask import Flask, Blueprint, render_template, flash, request, jsonify, redirect, url_for, send_file, session, make_response
from flask_login import login_required, current_user
from sqlalchemy import create_engine, exc, desc, asc
from sqlalchemy.sql import func
from .models import Note, Production, imported_sheets, flask_test, DISKS, BATCHES, VALIDATION, R2_Equipment_Checklist, MasterVerificationLog, B2B, B2B_Imported_Sheets, PC_Imported_Sheets, PC_Tech, UserData
from . import db, sqlEngine, validEngine, hddEngine
import json
import flask_excel as excel
import pandas as pandas
#import pymysql as pms
from .forms import ProductionSearchForm, SheetDeleteForm, TemplateDownloadForm, DateForm, ValidationEntryForm, EquipmentChecklistForm, ImportForm, AvatarForm
import os
from datetime import date
import plotly
import plotly.express as px
import qrcode
import website.helper_functions as hf
import numpy as np
from datetime import datetime
# from werkzeug.utils import secure_filename

testviews = Blueprint('testviews', __name__)

ROWS_PER_PAGE = 50


# views.py----------------------------------------------------------------------------
# Testing. For removing custom notes
# @testviews.route('/delete-note', methods=['POST'])
# def delete_note():
#     note = json.loads(request.data)
#     noteId = note['noteId']
#     note = Note.query.get(noteId)
#     if note:
#         if note.user_id == current_user.id:
#             db.session.delete(note)
#             db.session.commit()
#
#     return jsonify({})

# Unused=-=-=-=-=-=-=-=-=-=-=--=-=-==-=-=-=-=-=-=-=-=-=-=-==-=-=-=-=-=-=-====-=-=-==-=-=-=-=-=
# Testing. Can be used to download files.
# @testviews.route("/download", methods=['GET'])
# def download_file():
#     return excel.make_response_from_array([[1, 2], [3, 4]], "csv")

# Unused--------------------------------------------------------------------------------
# Testing. Exports whole database from Production as csv
# @testviews.route("/export", methods=['GET'])
# def doexport():
#     return excel.make_response_from_tables(db.session, [Production], "csv")

# Testing. Imports into testing Category table
# @testviews.route("/import_test", methods=['GET', 'POST'])
# def doimport():
#    if request.method == 'POST':

#        def category_init_func(row):
#            c = Category(row['name'])
#            c.catId = row['id']
#            return c

#        def post_init_func(row):
#            c = Category.query.filter_by(name=row['category']).first()
#            p = Post(row['title'], row['body'], c, row['pub_date'])
#            return p
#        request.save_book_to_database(
#            field_name='file', session=db.session,
#            tables=[Category, Post],
#            initializers=[category_init_func, post_init_func])
#        return redirect(url_for('.handson_table'), code=302)
#    return render_template('import_file.html', user=current_user)

# Testing. Pulls tables from Category and Post
# @testviews.route("/handson_view", methods=['GET'])
# def handson_table():
#    return excel.make_response_from_tables(
#        db.session, [Category, Post], 'handsontable.html')

#Testing. Test upload from network folder to database
'''
@testviews.route('/autoimport', methods=['GET', 'POST'])
def autoimport():
        
    dbConnection = sqlEngine.connect()

    df = pandas.read_excel(importFolder, names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability', 'Data Sanitization Field', 'Next Process Field', 'HDD MFG', 'HDD Serial #', 'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used', 'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)', 'Media', 'COA', 'Form Factor', 'Tech Initials', 'Date', 'Physical Condition/ Grade', 'AC Adapter Included', 'Screen Size', 'Test Result Codes', 'Battery Load Test', 'Original Design Battery Capacity', 'Battery Capacity @ Time of Test', 'Percent of Original Capacity', 'Battery Pass/Fail', 'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)', 'Sale Category'])
    
    try:
        frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)
    except ValueError as vx:
        print(vx)
    except Exception as ex:
        print(ex)
    else:
        print('Table imported successfully')
    finally:
        dbConnection.close()

        

    return render_template('import_pandas.html', shape = df.shape, user=current_user)
    #return redirect(url_for('.cycle_handson'), code=302)
    return render_template('import_pandas.html', user=current_user)
'''


# Unused-------------------------------------------------------------------------
# for displaying pandas dataframe as an HTML table
# @testviews.route('/pandas_table', methods=['GET', 'POST'])
# def pandastable():
#     if request.method == 'POST':
#
#         dbConnection = sqlEngine.connect()
#
#         sheetName = request.files['file'].filename
#
#         df = pandas.read_excel(request.files.get('file'), names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability', 'Data Sanitization Field', 'Next Process Field', 'HDD MFG', 'HDD Serial #', 'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used', 'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)', 'Media', 'COA', 'Form Factor', 'Tech Initials', 'Date', 'Physical Condition/ Grade', 'AC Adapter Included', 'Screen Size', 'Test Result Codes', 'Battery Load Test', 'Original Design Battery Capacity', 'Battery Capacity @ Time of Test', 'Percent of Original Capacity', 'Battery Pass/Fail', 'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)', 'Sale Category'])
#
#         df.loc[:,['sheet_id']] = sheetName
#
#         #add filename of imported file to imported_sheets table
#         newSheetRow = imported_sheets(sheetName=sheetName, importCheck=False)
#         db.session.add(newSheetRow)
#         db.session.commit()
#
#         table = df.to_html(classes='table')
#
#         try:
#             frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)
#         except ValueError as vx:
#             print(vx)
#         except Exception as ex:
#             print(ex)
#         else:
#             print('Table imported successfully')
#         finally:
#             dbConnection.close()
#
#
#
#         #return render_template('import_pandas.html', shape = df.shape, user=current_user)
#         #table is a variable in the sheet. Marked with "|safe" so that it renders as html, not as text.
#         return render_template('pandas_table.html', table=table, user=current_user)
#     return render_template('import_pandas.html', user=current_user)



# Testing. For adding sheet id to Production table, and removing sheetName if import fails
# @testviews.route('/safeimport', methods=['GET', 'POST'])
# def safeimport():
#    if request.method == 'POST':
#        
#        dbConnection = sqlEngine.connect()
#
#        sheetName = request.files['file'].filename
#
#        df = pandas.read_excel(request.files.get('file'), names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability', 'Data Sanitization Field', 'Next Process Field', 'HDD MFG', 'HDD Serial #', 'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used', 'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)', 'Media', 'COA', 'Form Factor', 'Tech Initials', 'Date', 'Physical Condition/ Grade', 'AC Adapter Included', 'Screen Size', 'Test Result Codes', 'Battery Load Test', 'Original Design Battery Capacity', 'Battery Capacity @ Time of Test', 'Percent of Original Capacity', 'Battery Pass/Fail', 'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)', 'Sale Category'])
#        
#        
#
# add filename of imported file to imported_sheets table
#        newSheetRow = imported_sheets(sheetName=sheetName, importCheck=False)
#        db.session.add(newSheetRow)

#        db.session.commit()

#        sheet = imported_sheets.query.filter_by(sheetName=sheetName).first()
#        sheetName_id = sheet.sheetID        

#        df.loc[:,['sheet_id']] = sheetName_id
#        print(sheetName_id)
        

#        table = df.to_html(classes='table')

#        try:
#            frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)
#        except ValueError as vx:
#            print(vx)
#            #undo the session changes (drop the sheetName)
#            db.session.rollback()
#        except Exception as ex:
#            print(ex)
            #undo the session changes (drop the sheetName)
#            db.session.rollback()
#        else:
#            print('Table imported successfully')
#        finally:
#            dbConnection.close()

        

        #return render_template('import_pandas.html', shape = df.shape, user=current_user)
        #table is a variable in the sheet. Marked with "|safe" so that it renders as html, not as text.
#        return render_template('pandas_table.html', table=table, user=current_user)
#    return render_template('import_pandas.html', user=current_user)


#views.py-------------------------------------------------------------------------------
# @testviews.route('/search', methods=['GET', 'POST'])
# def search():
#     prodForm = ProductionSearchForm()
#     if request.method == 'POST':
#         form = request.form
#         search_term = form['search']
#         select_term = form['select']
#         #formats string so that it can be passed to filter
#         search_format = {select_term: search_term}
#         results = Production.query.filter_by(**search_format).all()
#         #print(str(results))
#         return render_template('search.html', form=prodForm, results=results, user=current_user)
#     else:
#         return render_template('search.html', form=prodForm, user=current_user)

#Unused--------------------------------------------------------------------------------
#Not sure. Might be for uploading files to the database?
# @testviews.route('/upload', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         return jsonify({'result': request.get_array(field_name='file')})
#     return render_template('import_file.html', user=current_user)

#For viewing entire Production table. No limit function --> EDIT: Added limit function to 5000
# @testviews.route('/production')
# def production():
#     production_import = Production.query.limit(5000)
#     return render_template('production.html', user=current_user, proImport = production_import)

#Unused-=-=-=-==-=-=--=-=-=-=-=-=-=-=--==-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
#Import into production table
# @testviews.route("/import_crude", methods=['GET', 'POST'])
# def importToProduction():
#     if request.method == 'POST':
#
#         def production_init_func(row):
#             p = Production()
#             p.orderNo = row['ORDER NUMBER']
#             p.unitNo = row['UNIT #']
#             p.productName = row['PRODUCT NAME']
#             p.r2Applicability = row['R2 Applicability']
#             p.dataSanitizationField = row['Data Sanitization Field']
#             p.nextProcessField = row['Next Process Field']
#             p.hddMFG = row['HDD MFG']
#             p.hddSerialNo = row['HDD Serial #']
#             p.Manufacturer = row['MANUFACTURER']
#             p.Model = row['MODEL']
#             p.serialNo = row['SERIAL #']
#             p.asset = row['Asset']
#             p.newOrUsed = row['New/Used']
#             p.yearMFG = row['Year Manufactured']
#             p.processor = row['Processor']
#             p.speed = row['Speed']
#             p.ram = row['RAM (GB)']
#             p.hddSize = row['HDD (GB)']
#             p.media = row['Media']
#             p.coa = row['COA']
#             p.formFactor = row['Form Factor']
#             p.techInitials = row['Tech Initials']
#             p.date = row['Date']
#             p.grade = row['Physical Condition/ Grade']
#             p.acAdapterIncluded = row['AC Adapter Included']
#             p.screenSize = row['Screen Size']
#             p.testResultCodes = row['Test Result Codes']
#             p.batteryLoadTest = row['Battery Load Test']
#             p.originalDesignCap = row['Original Design Battery Capacity']
#             p.batCapAtTest = row['Battery Capacity @ Time of Test']
#             p.percentOrgCap = row['Percent of Original Capacity']
#             p.batteryPass = row['Battery Pass/Fail']
#             p.dataWipe = row['DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)']
#             p.saleCategory = row['Sale Category']
#             p.autoId = row['AutoID']
#             return p
#
#         request.save_book_to_database(
#             field_name='file', session=db.session,
#             tables=[Production],
#             initializers=[production_init_func])
#         return redirect(url_for('.cycle_handson'), code=302)
#     return render_template('import_file.html', user=current_user)

#Unused-------------------------------------------------------------------------
#Testing. For testing pandas
# @testviews.route('/pandas_test', methods=['GET', 'POST'])
# def pandastable_test():
#     if request.method == 'POST':
#
#         dbConnection = sqlEngine.connect()
#
#         sheetName = request.files['file'].filename
#
#         df = pandas.read_excel(request.files.get('file'), names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability', 'Data Sanitization Field', 'Next Process Field', 'HDD MFG', 'HDD Serial #', 'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used', 'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)', 'Media', 'COA', 'Form Factor', 'Tech Initials', 'Date', 'Physical Condition/ Grade', 'AC Adapter Included', 'Screen Size', 'Test Result Codes', 'Battery Load Test', 'Original Design Battery Capacity', 'Battery Capacity @ Time of Test', 'Percent of Original Capacity', 'Battery Pass/Fail', 'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)', 'Sale Category'])
#
#         df.loc[:,['sheet_id']] = sheetName
#
#         #add filename of imported file to imported_sheets table
#         newSheetRow = imported_sheets(sheetName=sheetName, importCheck=False)
#         db.session.add(newSheetRow)
#         db.session.commit()
#
#         try:
#             frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)
#         except ValueError as vx:
#             print(vx)
#         except Exception as ex:
#             print(ex)
#         else:
#             print('Table imported successfully')
#         finally:
#             dbConnection.close()
#
#
#
#         #return render_template('import_pandas.html', shape = df.shape, user=current_user)
#         return redirect(url_for('.cycle_handson'), code=302)
#     return render_template('import_pandas.html', user=current_user)

# Unused----------------------------------------------------------------------------
# @testviews.route('/pandas_search', methods=['GET', 'POST'])
# def pandasSearch():
#     prodForm = ProductionSearchForm()
#     if request.method == 'POST':
#         form = request.form
#         search_term = form['search']
#         select_term = form['select']

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




    #   results = Production.query.filter(getattr(Production, select_term).like('%{}%'.format(search_term)))
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



    #     if prodForm.downl.data:
    #         print('Download!')
    #         if select_term == 'orderNo':
    #             select_term = 'Order Number'
    #         elif select_term == 'productName':
    #             select_term = 'Product Name'
    #         elif select_term == 'serialNo':
    #             select_term = 'Serial Number'
    #         elif select_term == 'date':
    #             select_term = 'Date'
    #
    #         query_sets = db.session.execute('SELECT `Unit #` AS "Unit #",`Product Name` AS "Product Name", "NA" AS "HDD MFG", "NA" AS "HDD Serial #", `Manufacturer` AS "Manufacturer", `Model` AS "Model", `Serial Number` AS "Serial #", `Asset` AS "Asset", `Year Manufactured` AS "Year Manufactured", `Processor` AS Processor, `Speed` AS Speed, `RAM (GB)` AS RAM, `Media` AS Media, `COA` AS COA, `Form Factor` AS "Form Factor", "N/A" AS "HDD (GB)", `Test Result Codes` AS "TEST RESULT CODES (SEE TRANSLATIONS)", `Sale Category` AS "Sale Category" FROM Production WHERE `{0}` LIKE "%{1}%"'.format(select_term, search_term))
    #         column_names = ["Unit #", 'Product Name', "HDD MFG", "HDD Serial #", 'Manufacturer', 'Model', 'Serial #', "Asset", 'Year Manufactured', 'Processor', 'Speed', 'RAM', 'Media', 'COA', 'Form Factor', 'HDD (GB)', "TEST RESULT CODES (SEE TRANSLATIONS)", 'Sale Category']
    #         return excel.make_response_from_query_sets(query_sets, column_names, "csv")
    #     else:
    #         print('No Download!')
    #
    #
    #
    #
    #
    #
    #     return render_template('search.html', form=prodForm, results=results, user=current_user)
    # else:
    #     return render_template('search.html', form=prodForm, user=current_user)

#def query_db(select, search):
#    f = getattr(Production, select)
#    q = Production.query.filter((select))
#    return q.all()

# Unused/Under Construction --------------------------------------------------
# @testviews.route('/delete_sheet', methods=['GET', 'POST'])
# def delete_sheet():
#     delete_form = SheetDeleteForm()
#     if request.method == 'POST':
#         form = request.form
#         search_term = form['search']
#         select_term = form['select']
#
#         results = imported_sheets.query.filter(getattr(imported_sheets, select_term).like('%{}%'.format(search_term))).all()
#
#     else:
#         results = ''
#     print(str(results))
#     return render_template('search_sheets.html', form=delete_form, results=results, user=current_user)


#views.py---------------------------------------------------------
# @testviews.route('/templates', methods = ['GET', 'POST'])
# def download_templates():
#     template_form = TemplateDownloadForm()
#     if request.method == 'POST':
#         app = Flask(__name__)
#         form = request.form
#         #lt_button = form.laptop_template_download.data
#         #dt_button = form.desktop_template_download.data
#         #pro_button = form.processing_template_download.data
#         #lcd_button = form.lcd_template_download.data
#
#         if template_form.laptop.data:
#             file_path = os.path.join(app.root_path, 'excel_templates', 'PR-F52B Equipment Testing and Inventory Workbook MAIN.xlsx')
#             return send_file(file_path)
#             #print(str(file_path))
#             #print('LT check')
#         elif template_form.desktop_template_download.data:
#             file_path = os.path.join(app.root_path, 'excel_templates', 'PR-F52B Equipment Testing and Inventory Workbook Desktops.xlsx')
#             return send_file(file_path)
#         elif template_form.processing_template_download.data:
#             file_path = os.path.join(app.root_path, 'excel_templates', 'PR-F52B Equipment Testing and Inventory Workbook Processing.xlsx')
#             return send_file(file_path)
#         elif template_form.lcd_template_download.data:
#             file_path = os.path.join(app.root_path, 'excel_templates', 'PR-F52B Equipment Testing and Inventory Workbook LCDs.xlsx')
#             return send_file(file_path)
#
#     return render_template('excel_templates.html', form=template_form, user=current_user)

#Unused------------------------------------------------------------------------------
# @testviews.route('/hdd_test')
# def hdd_test():
#     '''For testing connection to db_killdisk database'''
#     test = flask_test.query.all()
#     return render_template('test.html', user=current_user, test=test)


#Unused--------------------------------------------------------------------
# @testviews.route('/hdd_date_test', methods=['GET', 'POST'])
# def hdd_date_test():
#     '''
#     For testing pulling HDD's in a date range.
#     Will be using the Batch start time so it is consistent for each batch.
#
#     Requires:
#     DateForm (forms.py)
#
#     '''
#     form = DateForm()
#     if form.validate_on_submit():
#         session['startdate'] = form.startdate.data
#         session['enddate'] = form.enddate.data
#         return redirect('test_date')
#     return render_template('test_date_index.html', form=form, user=current_user)


#Unused-----------------------------------------------------
# @testviews.route('/test_date', methods=['GET', 'POST'])
# def test_date():
#     '''For testing date values and displaying them on webpage.'''
#     startdate = session['startdate']
#     enddate = session['enddate']
#     return render_template('test_date.html', user=current_user)

#searchviews.py--------------------------------------------------------------
#Moved to searchviews
# @testviews.route('/hdd_search_test', methods=['GET', 'POST'])
# def hdd_search_test():
#     dateForm = DateForm()
#     result_count = None
#     batch_selection = []
#     if request.method == 'POST':
#
#         form = request.form
#         batch_selection = request.batchsel
#         start_date = form['startdate']
#         end_date = form['enddate']
#
#
#         #formats string so that it can be passed to filter
#         #search_query = f"SELECT * FROM DISKS WHERE BatchStarted BETWEEN '{start_date}' AND '{end_date}'"
#         #print(search_query)
#         #results = db.session.execute(search_query, bind=db.get_engine(app, 'hdd_db'))
#
#         #Filters HDD database to commonly used filters for production.
#         cur_result = DISKS.query\
#                 .filter(DISKS.BatchStarted\
#                 .between(start_date, end_date))
#         cur_result = cur_result.filter(DISKS.Process == 'E')
#         cur_result = cur_result.filter(DISKS.Progress == 100)
#
#         #Takes the result set and gets a list of only unique values.
#         distinct_results = cur_result.distinct(DISKS.OrderNo).all()
#         #distinct_results = db.session.query(DISKS.OrderNo).distinct().all()
#         #print(str(distinct_results))
#
#         result_count = f"Search returned {cur_result.count()} results"
#
#         #column_names = cur_result.column_descriptions
#
#         '''
#         This is to get column names for the returned result for cur_result.
#         Not super useful when pulling all columns, but will be useful when dynamically buidling sheets from selected columns
#         '''
#         column_names = cur_result.statement.columns.keys()
#         #print(column_names)
#
#         results = cur_result.all()
#
#         # AttributeError: 'list' object has no attribute 'headers' for below
#         # print(results.headers)
#
#         #print(str(results))
#         #print(str(result_count))
#         if dateForm.downl.data:
#             '''
#             For some reason, the "OS" column was used as the first column.
#             Skipped first column(OS) with [1:]. Doesn't display in download.
#             '''
#             return excel.make_response_from_query_sets(results, column_names[1:], "xlsx")
#
#
#         return render_template('hdd_search.html', distinct=distinct_results, form=dateForm, results=results, count=result_count, batchsel=batch_selection, column_names=column_names, user=current_user)
#     else:
#         return render_template('hdd_search.html', form=dateForm, user=current_user)


#--------------------------------------------------------------------------------------
# @testviews.route('/test_checkbox_batch_selection', methods=['GET', 'POST'])
# def test_batch_selection():
#     '''
#     For populating a list of checkboxes from batches pulled from a date range.
#     '''
#     dateForm = DateForm()
#     if request.method == 'POST':
#
#         form = request.form
#         start_date = form['startdate']
#         end_date = form['enddate']
#
#         batch_result = BATCHES.query\
#                         .filter(BATCHES.Started\
#                         .between(start_date, end_date))
#
#         batch_result = batch_result.all()
#
#         results = None
#
#         #print(batch_result)
#         return render_template('test_listboxes.html', form=dateForm, batches=batch_result, results=results, user=current_user)
#
#     else:
#         return render_template('test_checkboxes.html', form=dateForm, user=current_user)

#Testing. Unused-------------------------------------------------------------------------
# @testviews.route('/test_checkbox', methods=['GET', 'POST'])
# def test_checkbox():
#     if request.method == 'POST':
#         print(request.form.getlist('hello'))
#
#     return '''<form method="post">
#     <input type="checkbox" name="hello" value="world" checked>
#     <input type="checkbox" name="hello" value="dustinism" checked>
#     <input type="submit">
#     </form>
#     '''


# @testviews.route('/test_checkboxes_hdd_pass', methods=['GET', 'POST'])
# def test_hdd_pass():
#     '''
#     For testing splitting the batch selection into two functions.
#     Will only be called from test_batch_selection function.
#
#     This is step two of the process of searching for batches.
#     '''
#     dateForm = DateForm()
#
# #    if request.method == "POST":
# #        form1 = request.form['checkbox_form']
# #        print(request.form1.getlist("batch_checkboxes"))
#
# #        return render_template('test_listboxes.html', form=form1, user=current_user)
#
# #    else:
#     dateform = request.form['date_form']
#     start_date = dateform['startdate']
#     end_date = dateform['enddate']
#
#     batch_result = BATCHES.query\
#                         .filter(BATCHES.Started\
#                         .between(start_date, end_date))
#     batch_result = batch_result.filter(BATCHES.Process == 'E')
#     batch_result = batch_result.filter(BATCHES.Progress == 100)
#
#
#     batch_result = batch_result.all()
#
#     return render_template('test_listboxes.html', form=dateForm, batches=batch_result, user=current_user)


# @testviews.route('/test_checkbox_passthrough', methods=['GET', 'POST'])
# def test_checkbox_list():
#     requested_batches = request.form.getlist("batch_checkboxes")
#     print(requested_batches)
#     return render_template('home.html', user=current_user)

# ------------------==================--------------------======================---------------------=====

# @testviews.route('/test_verification_log_display', methods=['GET', 'POST'])
# def verification_display():
#     '''
#     For pulling the verfication log from the server and displaying it in the browser.
#
#     Will eventually add date ranges to search specific dates, but for now it returns all results.
#     '''

# -------------------================----------------------======================---------------------=====

# @testviews.route('/test_validation_log_entry', methods=['GET', 'POST'])
# def validation_addition():
#     '''
#     For adding a record to the validation log.
#     Date is filled automatically on the date entered.
#     Requires make, model, serialNo
#     '''
#     entryform = ValidationEntryForm()
#
#     if request.method == 'POST':
#         form = request.form
#         make_field = form['make']
#         model_field = form['model']
#         serial_field = form['serial']
#         initials_field = form['initials']
#
#         if not [x for x in (make_field, model_field, serial_field, initials_field) if x is None]:
#             try:
#                 record = VALIDATION(Make=make_field, Model=model_field, DiskSerial=serial_field,
#                                     Date=date.today(), Verification=initials_field)
#                 db.session.add(record)
#                 db.session.commit()
#                 print('\n\nUploaded!\n\n')
#                 flash('Validation entry added!', category='success')
#                 # db.get_engine(app, 'hdd_db').execute(record)
#
#             except AttributeError:
#                 # record = VALIDATION.add(Make=make_field, Model=model_field, DiskSerial=serial_field,
#                 # Date=date.today(), Verification=initials_field)
#                 # print(record)
#                 db.session.rollback()
#                 print('\n\nSomething is wrong with your data!\n\n')
#
#             except exc.IntegrityError:
#                 db.session.rollback()
#                 print('\n\nError! This could be duplicate information!\n\n')
#
#         else:
#             print('\n\nBad IF Statement!\n\n')
#
#     return render_template('test_validate_new.html', form=entryform, user=current_user)



# ------========---------============-----------==============----------------==============------------====
# @testviews.route('/validation_table', methods=['GET'])
# def validation_view():
#     records = VALIDATION.query.all()
#
#     return render_template('validation_table.html', form=records, user=current_user)


# _________________________________________________________________________________________________________________
# @testviews.route('/datavisualization')
# def notdash():
#     '''
#     This is a simple demonstration of data visualization in flask similar to another
#     package called dash.
#     '''
#     df = pandas.DataFrame({
#         'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges', 'Bananas'],
#         'Amount': [4, 1, 2, 2, 4, 5],
#         'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
#     })
#
#     fig = px.bar(df, x='Fruit', y='Amount', color='City', barmode='group')
#
#     graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#
#     return render_template('testing_notdash.html', graphJSON=graphJSON)


# @testviews.route('/equipmentChecklist', methods=['GET', 'POST'])
# @login_required
# def checklist():
#     """
#     For testing connections to eCommerce database using Mark's database (set in __init__.py). \n
#     Basic layout using test_equipmentchecklist.html. \n
#     Layout of table is temporary and will be renewed with new columns.
#     """
#
#     equip_check = EquipmentChecklistForm()
#     if request.method == 'POST':
#         form = request.form
#         manufact = form['manufacturer']
#         post_test = form['post_test']
#         if not [x for x in (form['manufacturer'], form['post_test']) if x is None]:
#             try:
#                 # print('RecordTest')
#                 record = R2_Equipment_Checklist(manufacturer=manufact, post=post_test, techName=current_user.id)
#                 db.session.add(record)
#                 db.session.commit()
#                 flash('Validation entry added!', category='success')
#                 # print(record.techName)
#                 # print(current_user)
#             except:
#                 print('Error! Try Again')
#             finally:
#                 print('Check the database!')
#
#     return render_template('test_equipmentchecklist.html', form=equip_check, user=current_user)


"""
@testviews.route('/hdd_search', methods=['GET', 'POST'])
def hdd_search():
    '''
    Search exact matches from db_killdisk Database.

    '''
    dateForm = DateForm()
    result_count = None
    if request.method == 'POST':
        form = request.form
        start_date = form['startdate']
        end_date = form['enddate']
        batch_search = form['batch']
        success = form['passOnly']
        sucTest = form['passTest']
        # success_bool = form.get('pass0nly').
        # formats string so that it can be passed to filter
        # search_query = f"SELECT * FROM DISKS WHERE BatchStarted BETWEEN '{start_date}' AND '{end_date}'"
        # print(search_query)
        # results = db.session.execute(search_query, bind=db.get_engine(app, 'hdd_db'))

        # Filters HDD database to commonly used filters for production.
        # cur_result = DISKS.query \
        #    .filter(DISKS.BatchStarted
        #           .between(start_date, end_date))
        # cur_result = cur_result.filter(DISKS.Process == 'E')
        # cur_result = cur_result.filter(DISKS.Progress == 100)

        print(start_date)
        print(sucTest)


        '''
        Takes the result set and gets a list of only unique values.
        '''
        #distinct_results = cur_result.distinct(DISKS.OrderNo).all()

        # These 2 are filters for production.
        # distinct_results = db.session.query(DISKS.OrderNo).distinct().all()
        # print(str(distinct_results))

        # Displays # of results returned
        #result_count = f"Search returned {cur_result.count()} results"

        # column_names = cur_result.column_descriptions

        '''
        This is to get column names for the returned result for cur_result.
        Not super useful when pulling all columns, but will be useful when dynamically building sheets from selected columns
        '''
        #column_names = cur_result.statement.columns.keys()
        # print(column_names)

        #results = cur_result.all()

        # AttributeError: 'list' object has no attribute 'headers' for below
        # print(results.headers)

        # print(str(results))
        # print(str(result_count))
        # if dateForm.downl.data:
        '''
        For some reason, the "OS" column was used as the first column.
        Skipped first column(OS) with [1:]. Doesn't display in download.
        '''
            # return excel.make_response_from_query_sets(results, column_names[1:], "xlsx")
            # return excel.make_response_from_query_sets(results, column_names[1:], "csv")

        return render_template('test_checkboxes.html', form=dateForm, user=current_user)

        # return render_template('test_checkboxes.html', distinct=distinct_results, form=dateForm, results=results,
        #                      count=result_count, column_names=column_names, user=current_user)

    else:
        return render_template('test_checkboxes.html', form=dateForm, user=current_user)
"""


# _______________-----------------------__________________----------------------_____________________---------------
# Pagination for HDD_Search
# @testviews.route('/hdd_search-pagination', methods=['GET', 'POST'])
# def hdd_search_pagination():
#     """
#     Search exact matches from db_killdisk Database.
#
#     """
#     ROWS_PER_PAGE = 50
#     dateForm = DateForm()
#     result_count = None
#
#     page = request.args.get('page', 1, type=int)
#
#     if request.method == 'POST':
#         form = request.form
#         start_date = form['startdate']
#         end_date = form['enddate']
#         # formats string so that it can be passed to filter
#         # search_query = f"SELECT * FROM DISKS WHERE BatchStarted BETWEEN '{start_date}' AND '{end_date}'"
#         # print(search_query)
#         # results = db.session.execute(search_query, bind=db.get_engine(app, 'hdd_db'))
#
#         # Filters HDD database to commonly used filters for production.
#         cur_result = DISKS.query \
#             .filter(DISKS.BatchStarted \
#                     .between(start_date, end_date))
#         # cur_result = cur_result.filter(DISKS.Process == 'E')
#         # cur_result = cur_result.filter(DISKS.Progress == 100)
#
#         '''
#         Takes the result set and gets a list of only unique values.
#         '''
#         # distinct_results = cur_result.distinct(DISKS.OrderNo).paginate()
#
#         # These 2 are filters for production.
#         # distinct_results = db.session.query(DISKS.OrderNo).distinct().all()
#         # print(str(distinct_results))
#
#         # Displays # of results returned
#         result_count = f"Search returned {cur_result.count()} results"
#
#         # column_names = cur_result.column_descriptions
#
#         '''
#         This is to get column names for the returned result for cur_result.
#         Not super useful when pulling all columns, but will be useful when dynamically buidling sheets from selected columns
#         '''
#
#         # print(column_names)
#
#         results = cur_result.paginate(per_page=ROWS_PER_PAGE, error_out=False)
#
#         # AttributeError: 'list' object has no attribute 'headers' for below
#         # print(results.headers)
#
#         # print(str(results))
#         # print(str(result_count))
#         if dateForm.downl.data:
#             '''
#             For some reason, the "OS" column was used as the first column.
#             Skipped first column(OS) with [1:]. Doesn't display in download.
#             '''
#             # return excel.make_response_from_query_sets(results, column_names[1:], "xlsx")
#             return excel.make_response_from_query_sets(cur_result.all(), column_names[1:], "csv")
#
#         # return render_template('test_hdd_search_paginate.html', form=dateForm, results=results,
#         #                       count=result_count, user=current_user)
#         return redirect(url_for('testviews.hdd_search_pagination', form=dateForm, results=results, count=result_count, user=current_user), code=307)
#     else:
#         return render_template('test_hdd_search_paginate.html', form=dateForm, user=current_user)


# ---------------------------------------------------------------------------------------------------
# @testviews.route('/paginate', methods=['GET', 'POST'])
# def paginate():
#     page = request.args.get('page', 1, type=int)
#     pagination = DISKS.query.filter(DISKS.Disk == '/dev/sda').paginate(
#         per_page=ROWS_PER_PAGE, error_out=False)
#     drives = pagination.items
#     # print(pagination.query)
#     # print("Found the page?")
#     # print(pagination.items)
#     return render_template('test_paginate_macro.html', results=drives, pagination=pagination, user=current_user)


# ----------------------------------------------------------------------------------------------------
# @testviews.route('/paginate-search', methods=['GET', 'POST'])
# @login_required
# def paginate_search():
#
#     if request.method == 'POST':
#         prev_form = request.form
#
#     form = DateForm()
#     result_count = None
#
#     page = request.args.get('page', 1, type=int)
#
#
#
#     if form.validate_on_submit():
#         print('submitted!')
#         # form = request.form
#         start_date = form.startdate.data
#         # form.startdate.data = ''
#         end_date = form.enddate.data
#         # form.enddate.data = ''
#
#         # formats string so that it can be passed to filter
#         # search_query = f"SELECT * FROM DISKS WHERE BatchStarted BETWEEN '{start_date}' AND '{end_date}'"
#         # print(search_query)
#         # results = db.session.execute(search_query, bind=db.get_engine(app, 'hdd_db'))
#
#         # Filters HDD database to commonly used filters for production.
#         cur_result = DISKS.query \
#             .filter(DISKS.BatchStarted \
#                 .between(start_date, end_date))
#         # cur_result = cur_result.filter(DISKS.Process == 'E')
#         # cur_result = cur_result.filter(DISKS.Progress == 100)
#
#         '''
#         Takes the result set and gets a list of only unique values.
#         '''
#         # distinct_results = cur_result.distinct(DISKS.OrderNo).all()
#
#         # These 2 are filters for production.
#         # distinct_results = db.session.query(DISKS.OrderNo).distinct().all()
#         # print(str(distinct_results))
#
#         # Displays # of results returned
#         result_count = f"Search returned {cur_result.count()} results"
#
#         # column_names = cur_result.column_descriptions
#
#         '''
#         This is to get column names for the returned result for cur_result.
#         Not super useful when pulling all columns, but will be useful when
#         dynamically building sheets from selected columns
#         '''
#         # column_names = cur_result.statement.columns.keys()
#         # print(column_names)
#
#         # results = cur_result.all()
#         pagination = cur_result.paginate(per_page=ROWS_PER_PAGE, error_out=False)
#
#         # AttributeError: 'list' object has no attribute 'headers' for below
#         # print(results.headers)
#
#         # print(str(results))
#         # print(str(result_count))
#         if form.downl.data:
#             '''
#             For some reason, the "OS" column was used as the first column.
#             Skipped first column(OS) with [1:]. Doesn't display in download.
#             '''
#             # return excel.make_response_from_query_sets(results, column_names[1:], "xlsx")
#             column_names = cur_result.statement.columns.keys()
#             results = cur_result.all()
#             return excel.make_response_from_query_sets(results, column_names[1:], "csv")
#
#         # print('Reached the redirect!')
#         print('validate form?')
#         return render_template('hdd_search.html', form=form, pagination=pagination,
#                                count=result_count, user=current_user)
#     else:
#         cur_result = session.get('cur_result')
#         if cur_result:
#             pagination = cur_result.paginate(per_page=ROWS_PER_PAGE, error_out=False)
#             print("PagiCheck")
#         else:
#             pagination = None
#             session['result_count'] = ''
#         return render_template('hdd_search.html', form=form, pagination=pagination,
#                                count=session.get('result_count'), user=current_user)


# ---------------------------------------------------------------------------------------------------------
# @testviews.route('/redirect-test', methods=['GET', 'POST'])
# def redirect_test():
#     form = DateForm()
#     page = request.args.get('page', 1, type=int)
#
#     if form.validate_on_submit():
#         # session['startdate'] = form.startdate.data
#         # print(session.get('startdate'))
#         cur_result = session.get('cur_result')
#         count = session.get('results_count')
#         session['results_count'] = ''
#         pagination = cur_result.paginate(ROWS_PER_PAGE, error_out=False)
#         return render_template('hdd_search.html', pagination=pagination, user=current_user)
#     else:
#         return render_template('hdd_search.html', form=form, user=current_user)


# -----------------------------------------------------------------------------------------------------
# @testviews.route('/passthrough', methods=['GET', 'POST'])
# def passthrough():
#     form = DateForm()
#
#     page = request.args.get('page', 1, type=int)
#
#     if form.validate_on_submit():
#         start_date = form.startdate.data
#         end_date = form.enddate.data
#
#         cur_result = DISKS.query.filter(DISKS.BatchStarted.between(start_date, end_date))
#
#         result_count = cur_result.count()
#
#         if form.downl.data:
#             column_names= cur_result.statement.columns.keys()
#             results = cur_result.all()
#             return excel.make_response_from_query_sets(results, column_names[1:], "csv")
#
#         return render_template('test_paginate_macro.html', form=form, pagination=cur_result.paginate(
#                             per_page=ROWS_PER_PAGE, error_out=False), count=result_count, user = current_user)
#
#     else:
#         pagination = None
#         return render_template('test_paginate_macro.html',form=form, pagination=pagination,
#                                user=current_user)


# ---------------------------------------------------------------------------------------------------------------------
# @testviews.route('/searchform', methods=['GET', 'POST'])
# def searchform_pass():
#     """
#     For paginating and displaying search results from the DISKS table.
#     Uses session variables to pass information.
#     """
#
#     form = DateForm()
#
#     page = request.args.get('page', 1, type=int)
#
#     if form.clear.data:
#         session.clear()
#         return redirect(url_for(request.endpoint))
#
#     if form.validate_on_submit():
#         session['start_date'] = str(form.startdate.data)
#         session['end_date'] = str(form.enddate.data)
#
#     if session.get('start_date'):
#         result_query = DISKS.query.filter(DISKS.BatchStarted.between(session['start_date'], session['end_date']))
#         cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
#         count = result_query.count()
#
#         if form.downl.data:
#             '''
#             For some reason, the "OS" column was used as the first column.
#             Skipped first column(OS) with [1:]. Doesn't display in download.
#             '''
#             return hf.download_current(result_query)
#
#         return render_template('hdd_search.html', form=form, pagination=cur_result, count=count, user=current_user)
#
#     return render_template('hdd_search.html', form=form, user=current_user)


# ----------------------------------------------------------------------------------------------------------------------
# @testviews.route('/searchdisplay', methods=['GET', 'POST'])
# def search_display():
#     """
#     For testing whether or not its feasible in this use case to separate the form and display
#     views of the search functions.
#     Spoiler: Its not really.
#     """
#
#     form = DateForm()
#
#     page = request.args.get('page', 1, type=int)
#
#     if form.validate_on_submit():
#         print('validated')
#
#         return render_template('test_paginate_macro.html', user=current_user)


# def helptest(search):
#     column_names = search.statement.column.keys()
#     print(column_names)



# @testviews.route('/hdd_search', methods=['GET', 'POST'])
# def hdd_search():
#
#     # Search exact matches from db_killdisk Database.
#
#
#     dateForm = DateForm()
#     result_count = None
#     page = request.args.get('page', 1, type=int)
#     if request.method == 'POST':
#         form = request.form
#         start_date = form['startdate']
#         end_date = form['enddate']
#
#         # formats string so that it can be passed to filter
#         # search_query = f"SELECT * FROM DISKS WHERE BatchStarted BETWEEN '{start_date}' AND '{end_date}'"
#         # print(search_query)
#         # results = db.session.execute(search_query, bind=db.get_engine(app, 'hdd_db'))
#
#         # Filters HDD database to commonly used filters for production.
#         cur_result = DISKS.query\
#                 .filter(DISKS.BatchStarted\
#                 .between(start_date, end_date))
#         # cur_result = cur_result.filter(DISKS.Process == 'E')
#         # cur_result = cur_result.filter(DISKS.Progress == 100)
#
#         '''
#         Takes the result set and gets a list of only unique values.
#         '''
#         distinct_results = cur_result.distinct(DISKS.OrderNo).all()
#
#         # These 2 are filters for production.
#         # distinct_results = db.session.query(DISKS.OrderNo).distinct().all()
#         # print(str(distinct_results))
#
#         # Displays # of results returned
#         result_count = f"Search returned {cur_result.count()} results"
#
#         #column_names = cur_result.column_descriptions
#
#         '''
#         This is to get column names for the returned result for cur_result.
#         Not super useful when pulling all columns, but will be useful when dynamically buidling sheets from selected columns
#         '''
#         # column_names = cur_result.statement.columns.keys()
#         # print(column_names)
#
#         # results = cur_result.all()
#         pagination = cur_result.paginate(per_page=ROWS_PER_PAGE, error_out=False)
#
#         # AttributeError: 'list' object has no attribute 'headers' for below
#         # print(results.headers)
#
#         # print(str(results))
#         # print(str(result_count))
#         if dateForm.downl.data:
#             '''
#             For some reason, the "OS" column was used as the first column.
#             Skipped first column(OS) with [1:]. Doesn't display in download.
#             '''
#             # return excel.make_response_from_query_sets(results, column_names[1:], "xlsx")
#             column_names = cur_result.statement.columns.keys()
#             results = cur_result.all()
#             return excel.make_response_from_query_sets(results, column_names[1:], "csv")
#
#         return render_template('hdd_search.html', form=dateForm, pagination=pagination, count=result_count, user=current_user)
#     else:
#         return render_template('hdd_search.html', form=dateForm, user=current_user)



# @testviews.route('/pandas_search', methods=['GET', 'POST'])
# @login_required
# def pandasSearch_test():
#     """
#            # For searching the Production Database.
#     """
#     prodForm = ProductionSearchForm()
#     if request.method == 'POST':
#         form = request.form
#         search_term = form['search']
#         select_term = form['select']
#
#         results = Production.query.filter(getattr(Production, select_term).like('%{}%'.format(search_term)))
#
#         if prodForm.downl.data:
#             print('Download!')
#             if select_term == 'orderNo':
#                 select_term = 'Order Number'
#             elif select_term == 'productName':
#                 select_term = 'Product Name'
#             elif select_term == 'serialNo':
#                 select_term = 'Serial Number'
#             elif select_term == 'date':
#                 select_term = 'Date'
#
#             query_sets = db.session.execute('SELECT `Unit #` AS "Unit #",`Product Name` AS "Product Name", "NA" AS "HDD MFG", "NA" AS "HDD Serial #", `Manufacturer` AS "Manufacturer", `Model` AS "Model", `Serial Number` AS "Serial #", `Asset` AS "Asset", `Year Manufactured` AS "Year Manufactured", `Processor` AS Processor, `Speed` AS Speed, `RAM (GB)` AS RAM, `Media` AS Media, `COA` AS COA, `Form Factor` AS "Form Factor", "N/A" AS "HDD (GB)", `Test Result Codes` AS "TEST RESULT CODES (SEE TRANSLATIONS)", `Sale Category` AS "Sale Category" FROM Production WHERE `{0}` LIKE "%{1}%"'.format(select_term, search_term))
#             column_names = ["Unit #", 'Product Name', "HDD MFG", "HDD Serial #", 'Manufacturer', 'Model', 'Serial #', "Asset", 'Year Manufactured', 'Processor', 'Speed', 'RAM', 'Media', 'COA', 'Form Factor', 'HDD (GB)', "TEST RESULT CODES (SEE TRANSLATIONS)", 'Sale Category']
#             return excel.make_response_from_query_sets(query_sets, column_names, "csv")
#         else:
#             print('No Download!')
#
#         result_count = f"Search returned {results.count()} results"
#
#         return render_template('search.html', form=prodForm, results=results, count=result_count, user=current_user)
#     else:
#         return render_template('search.html', form=prodForm, user=current_user)


# @testviews.route('/pandas_search_paginate', methods=['GET', 'POST'])
# def pandas_paginate():
#     form = ProductionSearchForm()
#     page = request.args.get('page', 1, type=int)
#
#     if form.clear.data:
#         session.clear()
#         redirect(url_for(request.endpoint))
#
#     if form.validate_on_submit():
#         session['production_select'] = form.select.data
#         session['production_search'] = form.search.data
#
#     if session.get('production_search'):
#         result_query = Production.query.filter\
#             (getattr(Production, session['production_select']).like\
#              ('%{}%'.format(session['production_search'])))
#         cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
#         count = result_query.count()
#
#         if form.downl.data:
#
#             df = pandas.read_sql(result_query.statement, result_query.session.bind)
#
#             resp = make_response(df.to_csv(index=False))
#             resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
#             resp.headers["Content-Type"] = "text/csv"
#             return resp
#
#         return render_template('search.html', form=form,
#                                pagination=cur_result, count=count, user=current_user)
#
#     return render_template('search.html', form=form, user=current_user)


# @testviews.route('/pandas_dataframe_production_test', methods=['GET', 'POST'])
# def pandas_df_test():
#     form = ProductionSearchForm()
#     page = request.args.get('page', 1, type=int)
#
#     if form.clear.data:
#         session.clear()
#         redirect(url_for(request.endpoint))
#
#     if form.validate_on_submit():
#         session['production_select'] = form.select.data
#         session['production_search'] = form.search.data
#
#     if session.get('production_search'):
#         result_query = Production.query.filter\
#             (getattr(Production, session['production_select']).like\
#              ('%{}%'.format(session['production_search'])))
#         cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
#         cur_df = pandas.read_sql(result_query.statement, result_query.session.bind)
#         count = result_query.count()
#
#         if form.downl.data:
#
#             resp = make_response(cur_df.to_csv(index=False))
#             resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
#             resp.headers["Content-Type"] = "text/csv"
#             return resp
#
#         return render_template('search.html', form=form,
#                                pagination=cur_df.to_html(), count=count, user=current_user)
#
#     return render_template('search.html', form=form, user=current_user)





# -------------------------------------------------------------------------------------------------


'''
@testviews.route('/site-map', methods=['GET', 'POST'])
def site_map():
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
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)
'''
# -----------------------------------------------------------------------------------------------

# @testviews.route('master_validation', methods=['GET', 'POST'])
# def master_validation():
#     """
#     For searching and displaying results from the Master Verification Log.
#
#     Requires:
#     helper_functions.py imported as hf
#
#
#     """
#
#     form = DateForm()
#
#     page = request.args.get('page', 1, type=int)
#
#     if form.clear.data:
#         session.clear()
#         return redirect (url_for(request.endpoint))
#
#     if form.validate_on_submit():
#         session['start_date'] = str(form.startdate.data)
#         session['end_date'] = str(form.enddate.data)
#
#     if session.get('start_date'):
#         result_query = MasterVerificationLog.query.filter(MasterVerificationLog.Date.between(session['start_date'], session['end_date']))
#         cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
#         count = result_query.count()
#
#         if form.downl.data:
#             return hf.download_verification_search(result_query)
#
#         return render_template('master_validation_table.html', form=form, pagination=cur_result, count=count, user=current_user)
#
#     return render_template('master_validation_table.html', form=form, user=current_user)


# ---------------------------------------------------------------------------------------------------------
# @testviews.route('validation_mass_import', methods=['GET', 'POST'])
# def validation_import():
#     """
#         For uploading validations to the new Validation log for all departments.
#         Needs to be moved to views.py and added to the validation navigation options
#     """
#
#     shape = ''
#     table = ''
#
#     if request.method == 'POST':
#
#         try:
#             with validEngine.connect() as dbConnection:
#                 columnNames = MasterVerificationLog.query.filter(MasterVerificationLog.autoID < 20).statement.columns.keys()
#                 print(columnNames)
#
#                 # columnNames = columnNames.append('autoID')
#
#                 # Need to remove autoID from the column names bc it is not included in the spreadsheet.
#                 # SQL will give these a value automatically when uploaded.
#                 columnNames.remove('autoID')
#
#                 # 'file' refers to the name of the input field from the HTML document
#                 df = pandas.read_excel(request.files.get('file'),
#                                        names=columnNames,
#                                        index_col=None)
#
#                 frame = df.to_sql("MasterVerificationLog", dbConnection, if_exists='append', index=False)
#
#         except ValueError as vx:
#             shape = vx
#         except Exception as ex:
#             shape = ex
#         else:
#             shape = f'Imported successfully with {frame} rows'
#             table = df.replace(np.nan, 'N/A').to_html(classes='table table-light')
#
#     return render_template('import_pandas.html', shape=shape, table=table, user=current_user)


# ----------------------------------------------------------------------------------------------------------------------

# @testviews.route('pandas_import_correction', methods=['GET', 'POST'])
# def pandas_import():
#
#     """
#         Purpose is to handle both the new and the old import templates, as of 10-31-22.
#
#     """
#
#     shape = ''
#     table = ''
#
#     if request.method == 'POST':
#
#
#
#
#         try:
#             with validEngine.connect() as dbConnection:
#
#                 # Get the filename from the 'file' id submitted through html.
#                 sheetName = request.files['file'].filename
#
#
#
#
#
#                 columnNames = Production.query.filter(
#                     Production.autoID < 20).statement.columns.keys()
#                 print(columnNames)
#
#                 # columnNames = columnNames.append('autoID')
#
#                 # Need to remove autoID from the column names bc it is not included in the spreadsheet.
#                 # SQL will give these a value automatically when uploaded.
#                 columnNames.remove('autoID')
#
#                 # 'file' refers to the name of the input field from the HTML document
#                 df = pandas.read_excel(request.files.get('file'),
#                                        names=columnNames,
#                                        index_col=None)
#
#                 frame = df.to_sql("MasterVerificationLog", dbConnection, if_exists='append', index=False)
#
#         except ValueError as vx:
#             shape = vx
#         except Exception as ex:
#             shape = ex
#         else:
#             shape = f'Imported successfully with {frame} rows'
#             table = df.replace(np.nan, 'N/A').to_html(classes='table table-light')
#
#     return render_template('import_pandas.html', shape=shape, table=table, user=current_user)


# --------------------------------------------------------------------------------------------------------

# @testviews.route('pandas_df_testing', methods=['GET', 'POST'])
# def pandas_testing():
#     shape = ''
#     table = ''
#     df = None
#     keys = ['Order Number', 'Unit #', 'Product Name', 'R2 Applicability', 'Data Sanitization Field', 'Next Process Field', 'HDD MFG', 'HDD Serial #', 'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used', 'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)', 'Media', 'COA', 'Form Factor', 'Tech Initials', 'Date', 'Cosmetic Condition / Grade', 'Functional Condition / Grade', 'AC Adapter Included', 'Screen Size', 'Test Result Codes', 'Battery Load Test', 'Original Design Battery Capacity', 'Battery Capacity @ Time of Test', 'Percent of Original Capacity', 'Battery Pass/Fail', 'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)', 'Sale Category']
#
#     old_column_one = "PHYSICAL CONDITION/ GRADE "
#     old_column_two = "PHYSICAL CONDITION / GRADE "
#     new_cosmetic_column = "COSMETIC CONDITION / GRADE "
#     new_functional_column = "FUNCTIONAL CONDITION / GRADE "
#
#     if request.method == 'POST':
#
#         sheetName = request.files['file'].filename
#
#         with validEngine.connect() as dbConnection:
#             df = pandas.read_excel(request.files.get('file'), names=keys, index_col=None)
#             try:
#
#                 # Uses the first row as the column headers so names do not have to be passed
#
#                 # Gets the column names of a dataframe
#                 column_names = list(df.columns.values)
#                 # print(column_names)
#
#                 physical_index = None
#
#                 if old_column_one in column_names:
#                     physical_index = column_names.index(old_column_one)
#                     print(physical_index)
#                     df.rename(columns={old_column_one: new_cosmetic_column}, inplace=True)
#                     df.insert(physical_index + 1, new_functional_column, value='')
#                 elif old_column_two in column_names:
#                     physical_index = column_names.index(old_column_two)
#                     print(physical_index)
#                     df.rename(columns={old_column_two: new_cosmetic_column}, inplace=True)
#
#                     # # Checks the index of the Physical Condition. Notice there is an extra space at the end.
#                     # physical_index = column_names.index(old_column_one)
#                     # physical_index_other = column_names.index(old_column_two)
#                     # print(physical_index_other)
#                     #
#                     # # Need to have inplace=True otherwise it will make a copy of dataframe!
#                     # df.rename(columns={old_column_one: new_cosmetic_column}, inplace=True)
#
#                     # Inserts the Functional Condition Column immediately after what is now the Cosmetic Condition
#                     df.insert(physical_index + 1, new_functional_column, value='')
#             except ValueError as vx:
#                 shape = str(vx)
#             except Exception as ex:
#                 shape = 'Exception!: ' + str(ex)
#
#             new_sheet_row = imported_sheets(sheetName=sheetName, importTime=datetime.now(), user_id=current_user.id)
#             db.session.add(new_sheet_row)
#             db.session.commit()
#
#             sheet = imported_sheets.query.filter_by(sheetName=sheetName).first()
#             sheet_name_id = sheet.sheetID
#
#             # This line adds a column to the end of the dataframe and assigns it a value.
#             df.loc[:, ['sheet_id']] = sheet_name_id
#
#             try:
#                 frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)
#             except ValueError as vx:
#                 sheet_name_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
#                 db.session.delete(sheet_name_query)
#                 db.session.commit()
#                 shape = vx
#             except Exception as ex:
#                 sheet_name_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
#                 db.session.delete(sheet_name_query)
#                 db.session.commit()
#                 shape = ex
#             else:
#                 shape = f'{sheetName} has imported successfully with {frame} rows'
#                 table = df.replace(np.nan, 'N/A').to_html(classes='table table-light')
#
#     return render_template('import_pandas.html', shape=shape, table=table, user=current_user)



# ---------------------------------------------------------------------------------------------------------------------

# For adding sheet id to Production table, and removing sheetName if import fails
# @testviews.route('/hdd_import', methods=['GET', 'POST'])
# def hddimport():
#     shape = ''
#     table = ''
#
#     form = ImportForm()
#
#     if request.method == 'POST':
#
#         dbConnection = hddEngine.connect()
#
#         sheetName = request.files['file'].filename
#
#         df = pandas.read_excel(request.files.get('file'), header=0, index_col=None)
#
#         try:
#             frame = df.to_sql("VALIDATION", dbConnection, if_exists='append', index=False)
#         except ValueError as vx:
#             shape = vx
#         except Exception as ex:
#             shape = ex
#         else:
#             shape = '{} has imported successfully with {} rows'.format(sheetName, frame)
#             table = df.replace(np.nan, 'N/A').to_html(classes='table table-dark')
#         finally:
#             dbConnection.close()
#
#         # return render_template('import_pandas.html', shape = df.shape, user=current_user)
#         # table is a variable in the sheet. Marked with "|safe" so that it renders as html, not as text.
#         # return render_template('pandas_table.html', table=table, user=current_user)
#     return render_template('import_pandas.html', shape=shape, table=table, form=form, user=current_user)


# ------------------------------------------------------------------------------------------------------

# @testviews.route('/pc_import', methods=['GET', 'POST'])
# def pcImport():
#
#     form = ImportForm()
#
#     shape = ''
#     table = ''
#
#     if request.method == 'POST':
#
#         sheetName = request.files['file'].filename
#
#         with sqlEngine.connect() as dbConnection:
#             if form.new_sheet_import.data or form.old_sheet_import.data:
#                 if PC_Imported_Sheets.query.filter_by(sheetName=sheetName).first():
#                     shape = 'This sheet has already been imported!'
#                     return render_template('import_pandas.html', form=form, shape=shape, table=table, user=current_user)
#
#                 try:
#
#                     column_names = PC_Tech.query.filter(PC_Tech.autoID < 20).statement.columns.keys()
#                     print(column_names)
#
#                     df = pandas.read_excel(request.files.get('file'),
#                         names=column_names,
#                         index_col=None)
#
#
#                     newSheetRow = PC_Imported_Sheets(sheetName=sheetName, importTime=datetime.now(), user_id=current_user.id)
#                     db.session.add(newSheetRow)
#                     db.session.commit()
#
#                     sheet = PC_Imported_Sheets.query.filter_by(sheetName=sheetName).first()
#                     sheet_name_id = sheet.sheetID
#
#
#
#                     df.loc[:, ['sheet_id']] = sheet_name_id
#
#                     # print(df)
#
#                     frame = df.to_sql("PC_Tech", dbConnection, if_exists='append', index=False)
#
#                 except ValueError as vx:
#                     sheet_name_query = PC_Imported_Sheets.query.filter_by(sheetName=sheetName).first()
#                     db.session.delete(sheet_name_query)
#                     db.session.commit()
#                     shape = vx
#
#                 except Exception as ex:
#                     sheet_name_query = PC_Imported_Sheets.query.filter_by(sheetName=sheetName).first()
#                     db.session.delete(sheet_name_query)
#                     db.session.commit()
#                     shape = ex
#
#                 else:
#                     shape = f'{sheetName} has imported successfully with {frame} rows'
#                     table = df.replace(np.nan, 'N/A').to_html(classes='table table-light')
#
#     return render_template('import_pandas.html', form=form, shape=shape, table=table, user=current_user)


# --------------------------------------------------------------------------------------------------------------------


# @testviews.route('/import_testing', methods=['GET', 'POST'])
# def import_test():
#
#     form = ImportForm()
#
#     shape = ''
#     table = ''
#
#
#     if request.method == "POST":
#
#         sheetName = request.files['file'].filename
#
#
#         df = pandas.read_excel(request.files.get('file'),
#                                                names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability',
#                                                       'Data Sanitization Field', 'Next Process Field', 'HDD MFG',
#                                                       'HDD Serial #',
#                                                       'Manufacturer', 'Model', 'Serial Number', 'Asset', 'Customer Name',
#                                                       'Sales Rep', 'New/Used',
#                                                       'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)',
#                                                       'Media', 'COA',
#                                                       'Form Factor', 'Tech Initials', 'Date', 'Cosmetic Condition / Grade',
#                                                       'Functional Condition / Grade', 'AC Adapter Included', 'Screen Size',
#                                                       'Test Result Codes', 'Battery Load Test',
#                                                       'Original Design Battery Capacity',
#                                                       'Battery Capacity @ Time of Test', 'Percent of Original Capacity',
#                                                       'Battery Pass/Fail',
#                                                       'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)',
#                                                       'Disposition', 'Power Supply', 'Motherboard/CPU', 'Hard Drive',
#                                                       'Memory', 'USB Ports', 'Peripheral Port', 'Card Reader',
#                                                       'Optical Drive', 'Screen', 'Screen Hinge', 'Trackpad', 'Keyboard',
#                                                       'Screen/Backlights'], index_col=None)
#
#
#
#         # df.to_csv('test_csv.csv', index=False)
#         with sqlEngine.connect() as dbConnection:
#             df.to_sql("Production", dbConnection, if_exists="append", index=False)
#
#     return render_template('import_pandas.html', form=form, shape=shape, table=table, user=current_user)



# @testviews.route('hdd_validation_table', methods=['GET', 'POST'])
# def hdd_validation():
#     """
#     For searching and displaying results from the Master Verification Log.
#
#     Requires:
#     helper_functions.py imported as hf
#
#
#     """
#     form = DateForm()
#
#     page = request.args.get('page', 1, type=int)
#
#     if form.clear.data:
#         session.clear()
#         return redirect (url_for(request.endpoint))
#
#     if form.validate_on_submit():
#         session['start_date'] = str(form.startdate.data)
#         session['end_date'] = str(form.enddate.data)
#
#     if session.get('start_date'):
#         result_query = VALIDATION.query.filter(VALIDATION.Date.between(session['start_date'], session['end_date']))
#         cur_result = result_query.paginate(page, per_page=ROWS_PER_PAGE, error_out=False)
#         count = result_query.count()
#
#         if form.downl.data:
#             return hf.download_verification_search(result_query)
#
#         return render_template('validation_table.html', form=form, pagination=cur_result, count=count, user=current_user)
#
#     return render_template('validation_table.html', form=form, user=current_user)


# --------------------------------------------------------------------------------------------------------------------

# # For adding sheet id to Production table, and removing sheetName if import fails
# @testviews.route('/pandas_import', methods=['GET', 'POST'])
# def safeimport():
#
#     form = ImportForm()
#
#     frame = None
#
#     shape = ''
#     table = ''
#
#     if request.method == 'POST':
#
#         sheetName = request.files['file'].filename
#
#         with sqlEngine.connect() as dbConnection:
#             if form.new_sheet_import.data:
#
#                 try:
#                     df = pandas.read_excel(request.files.get('file'),
#                                names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability',
#                                       'Data Sanitization Field', 'Next Process Field', 'HDD MFG', 'HDD Serial #',
#                                       'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used',
#                                       'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)', 'Media', 'COA',
#                                       'Form Factor', 'Tech Initials', 'Date', 'Cosmetic Condition / Grade',
#                                       'Functional Condition / Grade', 'AC Adapter Included', 'Screen Size',
#                                       'Test Result Codes', 'Battery Load Test', 'Original Design Battery Capacity',
#                                       'Battery Capacity @ Time of Test', 'Percent of Original Capacity',
#                                       'Battery Pass/Fail', 'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)',
#                                       'Sale Category'], index_col=None)
#                     newSheetRow = imported_sheets(sheetName=sheetName, importTime=datetime.now(), user_id=current_user.id)
#                     db.session.add(newSheetRow)
#                     db.session.commit()
#
#                     sheet = imported_sheets.query.filter_by(sheetName=sheetName).first()
#                     sheet_name_id = sheet.sheetID
#
#                     df.loc[:, ['sheet_id']] =sheet_name_id
#
#                     frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)
#
#                 except ValueError as vx:
#                     sheet_name_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
#                     db.session.delete(sheet_name_query)
#                     db.session.commit()
#                     shape = vx
#                 except Exception as ex:
#                     sheet_name_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
#                     db.session.delete(sheet_name_query)
#                     db.session.commit()
#                     shape = ex
#                 else:
#                     shape = f'{sheetName} has imported successfully with {frame} rows'
#                     table = df.replace(np.nan, 'N/A').to_html(classes='table table-light')
#
#             if form.old_sheet_import.data:
#                 try:
#                     old_column_one = "PHYSICAL CONDITION/ GRADE "
#                     old_column_two = "PHYSICAL CONDITION / GRADE "
#                     new_cosmetic_column = "Cosmetic Condition / Grade"
#                     new_functional_column = "Functional Condition / Grade"
#                     physical_index = None
#
#                     df = pandas.read_excel(request.files.get('file'),
#                                            names=['Order Number', 'Unit #', 'Product Name', 'R2 Applicability',
#                                                   'Data Sanitization Field', 'Next Process Field', 'HDD MFG',
#                                                   'HDD Serial #',
#                                                   'Manufacturer', 'Model', 'Serial Number', 'Asset', 'New/Used',
#                                                   'Year Manufactured', 'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)',
#                                                   'Media', 'COA',
#                                                   'Form Factor', 'Tech Initials', 'Date', 'PHYSICAL CONDITION/ GRADE ',
#                                                   'AC Adapter Included', 'Screen Size',
#                                                   'Test Result Codes', 'Battery Load Test',
#                                                   'Original Design Battery Capacity',
#                                                   'Battery Capacity @ Time of Test', 'Percent of Original Capacity',
#                                                   'Battery Pass/Fail',
#                                                   'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)',
#                                                   'Sale Category'], index_col=None)
#                     newSheetRow = imported_sheets(sheetName=sheetName, importTime=datetime.now(),
#                                                   user_id=current_user.id)
#                     db.session.add(newSheetRow)
#                     db.session.commit()
#
#                     sheet = imported_sheets.query.filter_by(sheetName=sheetName).first()
#                     sheet_name_id = sheet.sheetID
#
#                     column_names = list(df.columns.values)
#
#                     if old_column_one in column_names:
#                         physical_index = column_names.index(old_column_one)
#                         # print(physical_index)
#                         df.rename(columns={old_column_one: new_cosmetic_column}, inplace=True)
#                         df.insert(physical_index + 1, new_functional_column, value='')
#                     elif old_column_two in column_names:
#                         physical_index = column_names.index(old_column_two)
#                         # print(physical_index)
#                         df.rename(columns={old_column_two: new_cosmetic_column}, inplace=True)
#                         df.insert(physical_index + 1, new_functional_column, value='')
#
#                     df.loc[:, ['sheet_id']] = sheet_name_id
#
#                     frame = df.to_sql("Production", dbConnection, if_exists='append', index=False)
#
#                 except ValueError as vx:
#                     sheet_name_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
#                     db.session.delete(sheet_name_query)
#                     db.session.commit()
#                     shape = vx
#                 except Exception as ex:
#                     sheet_name_query = imported_sheets.query.filter_by(sheetName=sheetName).first()
#                     db.session.delete(sheet_name_query)
#                     db.session.commit()
#                     shape = ex
#                 else:
#                     shape = f'{sheetName} has imported successfully with {frame} rows'
#                     table = df.replace(np.nan, 'N/A').to_html(classes='table table-light')
#
#     return render_template('import_pandas.html', form=form, shape=shape, table=table, user=current_user)


# @testviews.route('/B2B_import', methods=['GET', 'POST'])
# def b2b_import():
#     """
#         For uploading Server and Switch spreadsheets in the database
#
#     """
#
#     form = ImportForm()
#
#     frame = None
#
#     shape = ''
#     table = ''
#
#     if request.method == 'POST':
#
#         sheetName = request.files['file'].filename
#
#         with sqlEngine.connect() as dbConnection:
#             if form.new_sheet_import.data or form.old_sheet_import.data:
#                 try:
#
#
#
#
#
#                     df = pandas.read_excel(request.files.get('file'),
#                                 names=['Order Number', 'Tech (Initials)', 'Date', 'Pallet', 'QTY', 'Asset',
#                                       'Product Name', 'R2 Applicability', 'Data Sanitization Field',
#                                       'Next Process Field', 'Manufacturer', 'Model', 'Faceplate?',
#                                       'Processor', 'Speed', 'RAM (GB)', 'HDD (GB)', 'Media', 'COA',
#                                       'Form Factor', 'AC Adaptor Port Functional', 'LCD Display',
#                                       'Disclosure to Buyer', 'Battery Load Test',
#                                       'Original Design Battery Capacity', 'Battery Capacity @ Time of Test',  '% of Original Capacity',
#                                       'Battery Pass/Fail', 'Serial #', 'Add-ons', 'Power Supply Info',
#                                       'Sale Category', 'New / Used', 'Year Manufactured', 'Cosmetic Condition / Grade',
#                                       'Functional Condition / Grade', 'DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)',
#                                       'Raid Controller', 'Switches/Buttons Functional',
#                                       'Hinges/Covers/Clasps', 'Power On Self-Test'], index_col=None)
#
#                     columnNames = B2B.query.filter(B2B.autoId < 20).statement.columns.keys()
#
#                     newSheetRow = B2B_Imported_Sheets(sheetName=sheetName, importTime=datetime.now(), user_id=current_user.id)
#                     db.session.add(newSheetRow)
#                     db.session.commit()
#
#                     sheet = B2B_Imported_Sheets.query.filter_by(sheetName = sheetName).first()
#                     sheet_name_id = sheet.sheet_id
#
#                     df.loc[:, ['sheet_id']] = sheet_name_id
#
#                     frame = df.to_sql("B2B", dbConnection, if_exists='append', index=False)
#
#                 except ValueError as vx:
#                     sheet_name_query = B2B_Imported_Sheets.query.filter_by(sheetName=sheetName).first()
#                     db.session.delete(sheet_name_query)
#                     db.session.commit()
#                     shape = vx
#
#                 except Exception as ex:
#                     sheet_name_query = B2B_Imported_Sheets.query.filter_by(sheetName=sheetName).first()
#                     db.session.delete(sheet_name_query)
#                     db.session.commit()
#                     shape = ex
#
#                 else:
#                     shape = f'{sheetName} has imported successfully with {frame} rows'
#                     table = df.replace(np.nan, 'N/A').to_html(classes='table table-light')
#
#     return render_template('import_pandas.html', form=form, shape=shape, table=table, user=current_user)


# @testviews.route('/b2b_search', methods=['GET', 'POST'])
# @login_required
# def b2b_search():
#     """
#     For paginating and displaying search results from the DISKS table.
#     Uses session variables to pass information.
#
#     Requires:
#     website.helper_functions.py for download function.
#     download function takes an unfinished query variable,
#     but is internal.
#     """
#
#     form = DateForm()
#
#     page = request.args.get('page', 1, type=int)
#
#     if form.clear.data:
#         session.clear()
#         return redirect(url_for(request.endpoint))
#
#     if form.validate_on_submit():
#         session['start_date'] = str(form.startdate.data)
#         session['end_date'] = str(form.enddate.data)
#
#     if session.get('start_date'):
#         result_query = B2B.query.filter(B2B.date.between(session['start_date'], session['end_date']))
#         cur_result = result_query.paginate(per_page=ROWS_PER_PAGE, error_out=False)
#         count = result_query.count()
#
#         if form.downl.data:
#             '''
#             For some reason, the "OS" column was used as the first column.
#             Skipped first column(OS) with [1:]. Doesn't display in download.
#
#             FUTURE EDIT: The download function works by matching variable names to the
#             names of the SQL columns. Therefore, model variable names must match its corresponding
#             column in the SQL table. The "OS" column must be skipped bc it is impossible to match that
#             column name in python (OS is a reserved variable). Luckily, it moved the problem column
#             to the front, so it can easily be skipped.
#
#             '''
#             return hf.download_hdd_search(result_query)
#
#         return render_template('b2b_search.html', form=form, pagination=cur_result, count=count, user=current_user)
#
#     return render_template('b2b_search.html', form=form, user=current_user)


# ----------------------------------------------------------------------------------------------------------------------
#@testviews.route('/servers', methods = ['GET'])
#@login_required
#@hf.user_permissions('Admin')
#def servers():

    #hosts = []
    #most_recent_results = []

    # for value in db.session.query(BATCHES.Host).distinct():
    #     print(value)
    #     last_upload = db.session.query(BATCHES).filter_by(BATCHES.Host==value).all()
    #     print(last_upload)
    #     # if last_upload.Started != None:
    #     #     hosts[value] = last_upload.Started
    #
    #     # print(hosts)
    #
    # # prior_batches = BATCHES.query.order_by(desc(BATCHES.Started)).limit(500)
    # # for value in BATCHES.query.distinct(DISKS.Host):
    # #     print(value)
    # #     last_upload = prior_batches.filter(BATCHES.Host==value).first()
    # #
    # #     hosts[value] = last_upload.Started
    # #
    # # print(hosts)

    # query = BATCHES.query.group_by(BATCHES.Host).order_by(desc(BATCHES.Finished))
    #
    # # print(most_recent_values)
    #
    # for result in query:
    #     latest_value = BATCHES.query.filter_by(Finished=result.Finished).first()
    #     try:
    #         hosts.append((latest_value.Host, latest_value.Finished.strftime("%m/%d/%Y %H:%M:%S")))
    #     except Exception as e:
    #         print(latest_value.Host, str(e))
    # print(hosts)

  #  get_hosts = BATCHES.query.group_by(BATCHES.Host)

   # for result in get_hosts:
       # hosts.append(result.Host)

    #for host in hosts:
       # try:
           # recent = BATCHES.query.filter_by(Host=host).order_by(desc(BATCHES.Finished)).first()
           # most_recent_results.append([host, recent.Finished.strftime("%m/%d/%Y %H:%M:%S"), recent.Batch])
        #except Exception as e:
           # print(host, str(e))

    #print(most_recent_results)

   # return render_template('servers.html', results=most_recent_results, user=current_user)

# ----------------------------------------------------------------------------------------------------------------------


@testviews.route('/upload_avatar', methods=['GET', 'POST'])
@login_required
@hf.user_permissions('Admin')
def upload_avatar():


    form = AvatarForm()
    # if form.validate_on_submit():
    #     print('Validated!')
    #     file = form.file.data
    #     if file:
    #         filename = secure_filename(file.filename)
    #         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #         file.save(filepath)
    #         image = UserData(user_id=current_user.id, filename=filename, path=filepath)
    #         db.session.add(image)
    #         db.session.commit()
    #         print("Image Uploaded!")
    #     else:
    #         print("Invalid File Type")
    # else:
    #     print('Did you submit?')


    if form.validate_on_submit():
        print('Testing')
        file = form.file.data

    else:
        file = None
    return render_template('test_avatar_upload.html', form=form, file=file, user=current_user)



# For checking if the filename of a file is secure.
# def allowed_filename(filename):
#     ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
#     return '.' in filename and \
#         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # return

@testviews.route('/qr-test', methods=["GET"])
def qr_test():
    text = "This is the text string"
    return render_template('qrtest.html', text=text, user=current_user)

































