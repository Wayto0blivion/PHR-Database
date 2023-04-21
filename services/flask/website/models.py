from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime, date
from sqlalchemy.dialects.mysql import TINYTEXT, TEXT, LONGTEXT


# Note homepage
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150), nullable=False)
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    sheets = db.relationship('imported_sheets')
    B2B_sheets = db.relationship('B2B_Imported_Sheets')
    # equip_check = db.relationship('R2_Equipment_Checklist')


class Production(db.Model):
    """
    Tracks what is uploaded by processing.

    No bind needed, located in default database
    """
    __tablename__ = 'Production'
    orderNo = db.Column('Order Number', db.String(25), nullable=False)
    unitNo = db.Column('Unit #', db.String(25), nullable=True)
    productName = db.Column('Product Name', db.String(50), nullable=False)
    r2Applicability = db.Column('R2 Applicability', db.String(12), nullable=False)
    dataSanitizationField = db.Column('Data Sanitization Field', db.String(12), nullable=False)
    nextProcessField = db.Column('Next Process Field', db.String(50), nullable=False)
    hddMFG = db.Column('HDD MFG', db.String(255), nullable = True)
    hddSerialNo = db.Column('HDD Serial #', db.String(255), nullable = True)
    Manufacturer = db.Column('Manufacturer', db.String(50), nullable=True)
    Model = db.Column('Model', db.String(50), nullable=True)
    serialNo = db.Column('Serial Number', db.String(100), nullable=True)
    asset = db.Column('Asset', db.String(50), nullable=True)
    customerName = db.Column('Customer Name', db.String(255), nullable=True)
    salesRep = db.Column('Sales Rep', db.String(255), nullable=True)
    newOrUsed = db.Column('New/Used', db.String(25), nullable=True)
    yearMFG = db.Column('Year Manufactured', db.Integer, nullable = True)
    processor = db.Column('Processor', db.String(50), nullable=True)
    speed = db.Column('Speed', db.String(12), nullable=True)
    ram = db.Column('RAM (GB)', db.Integer, nullable=True)
    hddSize = db.Column('HDD (GB)', db.String(25), nullable=True)
    media = db.Column('Media', db.String(50), nullable=True)
    coa = db.Column('COA', db.String(50), nullable=True)
    formFactor = db.Column('Form Factor', db.String(10), nullable=True)
    techInitials = db.Column('Tech Initials', db.String(10), nullable=True)
    date = db.Column('Date', db.String(25), nullable=True)
    cosmetic_grade = db.Column('Cosmetic Condition / Grade', db.String(25), nullable=True)
    functional_grade = db.Column('Functional Condition / Grade', db.String(25), nullable=True)
    acAdapterIncluded = db.Column('AC Adapter Included', db.String(5), nullable=True)
    screenSize = db.Column('Screen Size', db.Numeric(4,2), nullable=True)
    testResultCodes = db.Column('Test Result Codes', db.String(255), nullable=True)
    batteryLoadTest = db.Column('Battery Load Test', db.String(4), nullable=True)
    originalDesignCap = db.Column('Original Design Battery Capacity', db.String(20), nullable=True)
    batCapAtTest = db.Column('Battery Capacity @ Time of Test', db.String(20), nullable=True)
    percentOrgCap = db.Column('Percent of Original Capacity', db.String(12), nullable=True)
    batteryPass = db.Column('Battery Pass/Fail', db.String(4), nullable=True)
    dataWipe = db.Column('DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)', db.String(25), nullable=True)
    disposition = db.Column('Disposition', db.String(50), nullable=True)
    powerSupply = db.Column('Power Supply', db.String(8), nullable=True)
    motherboard = db.Column('Motherboard/CPU', db.String(8), nullable=True)
    hardDrive = db.Column('Hard Drive', db.String(8), nullable=True)
    memory = db.Column('Memory', db.String(8), nullable=True)
    usbPorts = db.Column('USB Ports', db.String(8), nullable=True)
    peripheralPort = db.Column('Peripheral Port', db.String(8), nullable=True)
    cardReader = db.Column('Card Reader', db.String(8), nullable=True)
    opticalDrive = db.Column('Optical Drive', db.String(8), nullable=True)
    screen = db.Column('Screen', db.String(8), nullable=True)
    screenHinge = db.Column('Screen Hinge', db.String(8), nullable=True)
    trackpad = db.Column('Trackpad', db.String(8), nullable=True)
    keyboard = db.Column('Keyboard', db.String(8), nullable=True)
    screenBacklights = db.Column('Screen/Backlights', db.String(8), nullable=True)
    autoId = db.Column('AutoID', db.Integer, primary_key=True)
    sheet_id = db.Column(db.Integer, db.ForeignKey('imported_sheets.sheetID'))
    importCheck = db.Column(db.Boolean, default=False)
    

class imported_sheets(db.Model):
    __tablename__ = 'imported_sheets'
    sheetID = db.Column(db.Integer, primary_key=True)
    sheetName = db.Column(db.String(255), unique=True)
    importTime = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sheetRel = db.relationship('Production')


class flask_test(db.Model):
    """
    Creates a model of a test table to check connection to db_killdisk

    bind: hdd_db
    """
    __bind_key__ = 'hdd_db'
    __tablename__= 'flask_test'
    id = db.Column('ID', db.Integer, primary_key=True)
    name = db.Column('Name', db.Integer)
    location = db.Column('Location', db.Integer)
    date = db.Column('Date', db.Integer)


class DISKS(db.Model):
    '''
    Creates a model of the 'DISKS' table in db_killdisk
    
    bind: hdd_db
    '''
    __bind_key__ = 'hdd_db'
    __tablename__ = 'DISKS'
    Disk = db.Column('Disk', db.String(50), primary_key=True)
    Started = db.Column('Started', db.DateTime(), primary_key=True)
    Process = db.Column('Process', db.String(3), nullable=True)
    Finished = db.Column('Finished', db.DateTime(), nullable=True)
    Elapsed = db.Column('Elapsed', db.String(12))
    BatchStarted = db.Column('BatchStarted', db.DateTime(), nullable=True)
    Batch = db.Column('Batch', db.String(50), nullable=True)
    Success = db.Column('Success', db.String(1), nullable=True)
    Status = db.Column('Status', db.String(1), nullable=True)
    Method = db.Column('Method', db.String(50), nullable=True)
    Passes = db.Column('Passes', db.Integer, nullable=True)
    VerifyPercent = db.Column('VerifyPercent', db.Integer, nullable=True)
    Progress = db.Column('Progress', db.Integer, nullable=True)
    InitDisk = db.Column('InitDisk', db.String(1), nullable=True)
    Fingerprint = db.Column('Fingerprint', db.String(255), nullable=True)
    Eject = db.Column('Eject', db.String(1), nullable=True)
    DiskSerial = db.Column('DiskSerial', db.String(25), nullable=True)
    DiskInfo = db.Column('DiskInfo', db.String(150), nullable=True)
    DiskRevision = db.Column('DiskRevision', db.String(20), nullable=True)
    DiskSizeStr = db.Column('DiskSizeStr', db.String(20), nullable=True)
    DiskSize = db.Column('DiskSize', db.Integer, nullable=True)
    DiskSectors = db.Column('DiskSectors', db.Integer, nullable=True)
    DiskBPS = db.Column('DiskBPS', db.Integer, nullable=True)
    DiskBay = db.Column('DiskBay', db.String(50), nullable=True)
    DiskPort = db.Column('DiskPort', db.String(15), nullable=True)
    PartNum = db.Column('PartNum', db.Integer, nullable=True)
    PartInfo = db.Column('PartInfo', db.String(255), nullable=True)
    WipeUnused = db.Column('WipeUnused', db.String(1), nullable=True)
    WipeMeta = db.Column('WipeMeta', db.String(1), nullable=True)
    WipeSlack = db.Column('WipeSlack', db.String(1), nullable=True)
    ExamType = db.Column('ExamType', db.String(1), nullable=True)
    CloneImage = db.Column('CloneImage', db.String(255), nullable=True)
    CertFile = db.Column('CertFile', db.String(255), nullable=True)
    XmlFile = db.Column('XmlFile', db.String(255), nullable=True)
    Technician = db.Column('Technician', db.String(100), nullable=True)
    Notes = db.Column('Notes', db.String(255), nullable=True)
    OrderNo = db.Column('OrderNo', db.String(50), nullable=True)
    Provider = db.Column('Provider', db.String(50), nullable=True)
    ProviderVer = db.Column('ProviderVer', db.String(10), nullable=True)
    OperSys = db.Column('OS', db.String(50), nullable=True)
    Build = db.Column('Build', db.String(20), nullable=True)
    Host = db.Column('Host', db.String(50), nullable=True)
    ErrCode = db.Column('ErrCode', db.Integer, nullable=True)
    ErrMsg = db.Column('ErrMsg', db.String(255), nullable=True)
    ErrCount = db.Column('ErrCount', db.Integer, nullable=True)


class BATCHES(db.Model):
    """
    Creates a model to connect to the BATCHES table of db_killdisk

    bind: hdd_db
    """
    __bind_key__='hdd_db'
    __tablename__='BATCHES'
    Batch = db.Column('Batch', db.String(50), primary_key=True)
    Started = db.Column('Started', db.DateTime(), primary_key=True)
    Process = db.Column('Process', db.String(3), nullable=True)
    Finished = db.Column('Finished', db.DateTime(), nullable=True)
    Elapsed = db.Column('Elapsed', db.String(12), nullable=True)
    Disks = db.Column('Disks', db.Integer, nullable=True)
    DisksFailed = db.Column('DisksFailed', db.Integer, nullable=True)
    DisksComplete = db.Column('DisksComplete', db.Integer, nullable=True)
    Success = db.Column('Success', db.String(1), nullable=True)
    Status = db.Column('Status', db.String(1), nullable=True)
    Method = db.Column('Method', db.String(50), nullable=True)
    Passes = db.Column('Passes', db.Integer, nullable=True)
    VerifyPercent = db.Column('VerifyPercent', db.Integer, nullable=True)
    Progress = db.Column('Progress', db.Integer, nullable=True)
    InitDisk = db.Column('InitDisk', db.String(1), nullable=True)
    Fingerprint = db.Column('Fingerprint', db.String(255), nullable=True)
    Eject = db.Column('Eject', db.String(1), nullable=True)
    WipeUnused = db.Column('WipeUnused', db.String(1), nullable=True)
    WipeMeta = db.Column('WipeMeta', db.String(1), nullable=True)
    WipeSlack = db.Column('WipeSlack', db.String(1), nullable=True)
    ExamType = db.Column('ExamType', db.String(1), nullable=True)
    CloneImage = db.Column('CloneImage', db.String(255), nullable=True)
    CertFile = db.Column('CertFile', db.String(255), nullable=True)
    XmlFile = db.Column('XmlFile', db.String(255), nullable=True)
    Technician = db.Column('Technician', db.String(100), nullable=True)
    Notes = db.Column('Notes', db.String(255), nullable=True)
    OrderNo = db.Column('OrderNo', db.String(50), nullable=True)
    Provider = db.Column('Provider', db.String(50), nullable=True)
    ProviderVer = db.Column('ProviderVer', db.String(10), nullable=True)
    OperSys = db.Column('OS', db.String(50), nullable=True)
    Build = db.Column('Build', db.String(20), nullable=True)
    Host = db.Column('Host', db.String(50), nullable=True)
    ErrCode = db.Column('ErrCode', db.Integer, nullable=True)
    ErrMsg = db.Column('ErrMsg', db.String(255), nullable=True)
    ErrCount = db.Column('ErrCount', db.Integer, nullable=True)


class VALIDATION(db.Model):
    """
    For verifying erasure of HDDs.

    bind = 'hdd_db'
    """
    __bind_key__='hdd_db'
    __tablename__='VALIDATION'
    DiskInfo = db.Column('DiskInfo', db.String(255))
    DiskSerial = db.Column('DiskSerial', db.String(50), primary_key=True)
    Sanitized = db.Column('Sanitized', db.Boolean, default=True, nullable=False)
    Date = db.Column('Date', db.DateTime, default=date.today())
    Verification = db.Column('Verification', db.String(4))


class R2_Equipment_Checklist(db.Model):
    """
    Equipment testing database for eComm

    bind='r2_db'
    """
    __bind_key__ = 'r2_db'
    __tablename__ = 'R2_Equipment_Checklist'
    autoID = db.Column('autoID', db.Integer, primary_key=True)
    creator = db.Column('Creator', db.Integer, db.ForeignKey('user.id'))
    description = db.Column('Description', db.String(255))
    manufacturer = db.Column('Manufacturer', TINYTEXT)
    model = db.Column('Model', TINYTEXT)
    yearMfg = db.Column('Year Mfg.', db.String(24))
    countryMfg = db.Column('Country of Mfg.', db.String(24))
    serials = db.Column('Serial Numbers', db.String(512))
    r2Applicability = db.Column('R2 Applicability', db.String(12))
    dataSanitization = db.Column('Data Sanitization', db.String(16))
    nextProcess = db.Column('Next Process', db.String(16))
    equipType = db.Column('Type of Equipment', db.String(56))
    physicalCondition = db.Column('Physical Condition', db.Integer)
    post = db.Column('POST', TINYTEXT)
    adapter = db.Column('AC Adapter Charges Battery', TINYTEXT)
    batLoadTest = db.Column('Battery Load Test', TINYTEXT)
    orgCap = db.Column('Original Capacity (mah)', db.Integer)
    testCap = db.Column('Capacity at Time of Test', db.Integer)
    percentCap = db.Column('Percentage of Original Capacity', db.Float)
    keyMouse = db.Column('Keyboard/Mouse Function', TINYTEXT)
    speaker = db.Column('Speaker Functionality', TINYTEXT)
    hinges = db.Column('Hinges, Covers, Clasps', TINYTEXT)
    display = db.Column('LCD/Display', TINYTEXT)
    screenTest = db.Column('Black/White Screen Test', TINYTEXT)
    dataWipe = db.Column('Data Wipe/Sanitize Complete', TINYTEXT)
    crt = db.Column('Secure CRT Test', TINYTEXT)
    selfTest = db.Column('Self/Internal Testing', TINYTEXT)
    portTest = db.Column('IP Port Test', TINYTEXT)
    poeTest = db.Column('POE Test', TINYTEXT)
    knobTest = db.Column('Knob/Button Functionality', TINYTEXT)
    digitizer = db.Column('Digitizer/Display Inspection', TINYTEXT)
    pths = db.Column('POST to Home Screen', TINYTEXT)
    testPage = db.Column('Test Page Print', TINYTEXT)
    other = db.Column('Other', TINYTEXT)
    otherTests = db.Column('Other (Tests)', db.String(255))
    status = db.Column('Status', TINYTEXT)
    saleCat = db.Column('Sale Category', db.String(64))
    disclosure = db.Column('Disclosure to Buyer', db.String(512))
    # zip = db.Column()
    quantity = db.Column('Quantity', db.Integer)
    techNotes = db.Column('Tech Notes', db.Text)
    date = db.Column('Date of Testing', db.Date)
    modified = db.Column('Last Modified', db.DateTime)
    modifier = db.Column('Modified By', db.Integer, db.ForeignKey('user.id'))


class MasterVerificationLog(db.Model):
    """
    Master Verification log from Validation Database.
    Variable name has to match the same as the column name in SQL for download function
    to work correctly.

    bind: validation_db
    table name: MasterVerificationLog
    """
    __bind_key__ = 'validation_db'
    __tablename__ = 'MasterVerificationLog'

    ProductType = db.Column('ProductType', db.String(255))
    SerialNumber = db.Column('SerialNumber', db.String(64))
    VisualInspection = db.Column('VisualInspection', db.Boolean, default=True, nullable=False)
    Retest = db.Column('Retest', db.Boolean, default=True, nullable=False)
    StatusVerification = db.Column('StatusVerification', db.Boolean, default=True, nullable=False)
    DataSanitizationVerified = db.Column('DataSanitizationVerified', db.Boolean, default=True, nullable=False)
    Date = db.Column('Date', db.Date)
    Initials = db.Column('Initials', db.String(4))
    NonconformityNotes = db.Column('NonconformityNotes', TEXT, nullable=True)
    Department = db.Column('Department', db.String(64))
    autoID = db.Column('autoID', db.Integer, primary_key=True)

'''
class R2_Equipment_Checklist(db.Model):
    """
    eComm Database
    Short test to verify entry is working
    bind = 'r2_db'
    """
    __bind_key__ = 'r2_db'
    __tablename__ = 'R2_Equipment_Checklist'
    autoID = db.Column('autoID', db.Integer, primary_key=True)
    manufacturer = db.Column('Manufacturer', db.String(48))
    post = db.Column('POST', db.String(3))
    techName = db.Column('Tech Name', db.String(), db.ForeignKey('user.id'))
'''






class B2B(db.Model):
    """
    Tracks what is uploaded by B2B (Switches and servers)

    Uses default binds so that I could import in as short a time as possible.
    """
    __tablename__ = 'B2B'
    orderNo = db.Column('Order Number', db.String(10), nullable=True)
    techInitials = db.Column('Tech (Initials)', db.String(10), nullable=False)
    date = db.Column('Date', db.Date, nullable=True)
    pallet = db.Column('Pallet', db.String(4), nullable=True)
    qty = db.Column('QTY', db.Integer, nullable=True)
    asset = db.Column('Asset', db.String(32), nullable=True)
    productName = db.Column('Product Name', db.String(64), nullable=False)
    r2Applicability = db.Column('R2 Applicability', db.String(4), nullable=False)
    dataSanitizationField = db.Column('Data Sanitization Field', db.String(4), nullable=False)
    nextProcessField = db.Column('Next Process Field', db.String(32), nullable=False)
    Manufacturer = db.Column('Manufacturer', db.String(64), nullable=True)
    Model = db.Column('Model', db.String(64), nullable=True)
    faceplate = db.Column('Faceplate?', db.String(8), nullable=True)
    processor = db.Column('Processor', db.String(64), nullable=True)
    speed = db.Column('Speed', db.Integer, nullable=True)
    ram = db.Column('RAM (GB)', db.String(64), nullable=True)
    hddSize = db.Column('HDD (GB)', db.String(64), nullable=True)
    media = db.Column('Media', db.String(32), nullable=True)
    coa = db.Column('COA', db.String(8), nullable=True)
    formFactor = db.Column('Form Factor', db.String(32), nullable=True)
    acAdaptor = db.Column('AC Adaptor Port Functional', db.String(8), nullable=True)
    lcd = db.Column('LCD Display', db.String(32), nullable=True)
    disclosure = db.Column('Disclosure to Buyer', db.String(256), nullable=True)
    batteryLoadTest = db.Column('Battery Load Test', db.String(32), nullable=True)
    originalDesignCap = db.Column('Original Design Battery Capacity', db.String(32), nullable=True)
    batCapAtTest = db.Column('Battery Capacity @ Time of Test', db.String(32), nullable=True)
    percentOrgCap = db.Column('% of Original Capacity', db.String(8), nullable=True)
    batteryPass = db.Column('Battery Pass/Fail', db.String(8), nullable=True)
    serialNo = db.Column('Serial #', db.String(64), nullable=True)
    addOns = db.Column('Add-ons', db.String(64), nullable=True)
    powerSupply = db.Column('Power Supply Info', db.String(64), nullable=True)
    saleCategory = db.Column('Sale Category', db.String(32), nullable=True)
    yearMFG = db.Column('Year Manufactured', db.String(32), nullable=True)
    newUsed = db.Column('New / Used', db.String(8), nullable=True)
    cosmetic_grade = db.Column('Cosmetic Condition / Grade', db.String(8), nullable=True)
    functional_grade = db.Column('Functional Condition / Grade', db.String(8), nullable=True)
    dataWipe = db.Column('DATA WIPE/ SANITIZE COMPLETE/ HDD FUNCTIONAL(PASS/FAIL)', db.String(32), nullable=True)
    raid = db.Column('Raid Controller', db.String(64), nullable=True)
    buttons = db.Column('Switches/Buttons Functional', db.String(8), nullable=True)
    hinges = db.Column('Hinges/Covers/Clasps', db.String(8), nullable=True)
    post = db.Column('Power On Self-Test', db.String(8), nullable=True)
    autoId = db.Column('autoID', db.Integer, primary_key=True)
    sheet_id = db.Column(db.Integer, db.ForeignKey('B2B_Imported_Sheets.sheet_id'))


class B2B_Imported_Sheets(db.Model):
    __tablename__ = 'B2B_Imported_Sheets'
    sheet_id = db.Column(db.Integer, primary_key=True)
    sheetName = db.Column(db.String(255), unique=True)
    importTime = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sheetRel = db.relationship('B2B')


class PC_Imported_Sheets(db.Model):
    __tablename__ = 'PC_Imported_Sheets'
    sheetID = db.Column('sheetID', db.Integer, primary_key=True)
    sheetName = db.Column('sheetName', db.String(255), unique=True)
    importTime = db.Column('importTime', db.DateTime, default=datetime.now())
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
    sheetRel = db.relationship('PC_Tech')


class PC_Tech(db.Model):
    __tablename__='PC_Tech'
    orderNo = db.Column('Order Number', db.String(25), nullable=False)
    unit = db.Column('Unit #', db.String(255), nullable=True)
    product = db.Column('Product Name', db.String(50), nullable=False)
    r2Applicability = db.Column('R2 Applicability', db.String(12), nullable=False)
    dataSanitizationField = db.Column('Data Sanitization Field', db.String(5), nullable=False)
    nextProcessField = db.Column('Next Process Field', db.String(50), nullable=False)
    hddMFG = db.Column('HDD MFG', db.String(255), nullable=True)
    hddSerial = db.Column('HDD Serial #', db.String(255), nullable=True)
    manufacturer = db.Column('Manufacturer', db.String(50), nullable=True)
    model = db.Column('Model', db.String(50), nullable=True)
    serialNo = db.Column('Serial Number', db.String(100), nullable=True)
    asset = db.Column('Asset', db.String(50), nullable=True)
    customerName = db.Column('Customer Name', db.String(255), nullable=True)
    salesRep = db.Column('Sales Rep', db.String(64), nullable=True)
    newUsed = db.Column('New/Used', db.String(25), nullable=True)
    yearMFG = db.Column('Year Manufactured', db.Integer, nullable=True)
    processor = db.Column('Processor', db.String(50), nullable=True)
    speed = db.Column('Speed (GHz)', db.String(12), nullable=True)
    ram = db.Column('RAM (GB)', db.Integer, nullable=True)
    hdd = db.Column('HDD (GB)', db.String(25), nullable=True)
    media = db.Column('Media', db.String(50), nullable=True)
    coa = db.Column('COA', db.String(50), nullable=True)
    formFactor = db.Column('Form Factor', db.String(10), nullable=True)
    techInitials = db.Column('Tech Initials', db.String(10), nullable=True)
    date = db.Column('Date', db.Date, nullable=True)
    cosmeticCondition = db.Column('Cosmetic Condition / Grade', db.String(25), nullable=True)
    functionalCondition = db.Column('Functional Condition / Grade', db.String(25), nullable=True)
    acAdapter = db.Column('AC Adapter Included', db.String(5), nullable=True)
    screenSize = db.Column('Screen Size', db.String(8), nullable=True)
    testResults = db.Column('Test Result Codes', db.String(255), nullable=True)
    batteryLoadTest = db.Column('Battery Load Test', db.String(4), nullable=True)
    originalBattery = db.Column('Original Design Battery Capacity', db.String(20), nullable=True)
    batCap = db.Column('Battery Capacity @ Time of Test', db.String(20), nullable=True)
    percentCap = db.Column('Percent of Original Capacity', db.String(12), nullable=True)
    batteryPass = db.Column('Battery Pass/Fail', db.String(4), nullable=True)
    dataWipe = db.Column('DATA WIPE / SANITIZE COMPLETE', db.String(25), nullable=True)
    saleCategory = db.Column('Sale Category', db.String(50), nullable=True)
    powerSupply = db.Column('Power Supply', db.String(4), nullable=True)
    motherboard = db.Column('Motherboard/CPU', db.String(4), nullable=True)
    hardDrivePass = db.Column('Hard Drive', db.String(4), nullable=True)
    memory = db.Column('Memory', db.String(4), nullable=True)
    usbPorts = db.Column('USB Ports', db.String(4), nullable=True)
    peripheral = db.Column('Peripheral Ports', db.String(4), nullable=True)
    cardReader = db.Column('Card Reader', db.String(4), nullable=True)
    opticalPass = db.Column('Optical Drive', db.String(4), nullable=True)
    screenPass = db.Column('Screen', db.String(4), nullable=True)
    screenHinge = db.Column('Screen Hinge', db.String(4), nullable=True)
    trackpad = db.Column('Trackpad', db.String(4), nullable=True)
    keyboard = db.Column('Keyboard', db.String(4), nullable=True)
    screenBacklights = db.Column('Screen/Backlights', db.String(4), nullable=True)
    autoID = db.Column('autoID', db.Integer, primary_key=True)
    sheet_id = db.Column('sheet_id', db.Integer, db.ForeignKey('PC_Imported_Sheets.sheetID'))











# Flask-Excel Testing

# class Post(db.Model):
#    postId = db.Column(db.Integer, primary_key=True)
#    title = db.Column(db.String(80))
#    body = db.Column(db.Text)
#    pub_date = db.Column(db.DateTime)

#    category_id = db.Column(db.Integer, db.ForeignKey('category.catId'))
#    category = db.relationship('Category',
#        backref=db.backref('posts',
#        lazy='dynamic'))

#    def __init__(self, title, body, category, pub_date=None):
#        self.title = title
#        self.body = body
#        if pub_date is None:
#            pub_date = datetime.utcnow()
#        self.pub_date = pub_date
#        self.category = category

#    def __repr__(self):
#        return '<Post %r>' % self.title


# class Category(db.Model):
#    catId = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(50))

#    def __init__(self, name):
#        self.name = name

#    def __repr__(self):
#        return '<Category %r>' % self.name

# class SampleTest(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(50))
#    surname = db.Column(db.String(50))
