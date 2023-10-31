from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import StringField, SelectField, DateField, SubmitField, RadioField, BooleanField, IntegerField, TextAreaField, PasswordField
# from wtforms import validators
from wtforms.validators import DataRequired, Optional, EqualTo, InputRequired, Length
from wtforms.widgets import TextArea, FileInput

"""

"""


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UserProfileForm(FlaskForm):
    """
    User Profile Form
    For updating user passwords
    """
    current_password = PasswordField('Current Password', validators=[InputRequired()])
    new_password = PasswordField('New Password', validators=[Length(min=7, message='Too short!')])
    new_password_verify = PasswordField('Verify New Password', validators=[InputRequired(), EqualTo('new_password', message='Password Mismatch!')])
    submit = SubmitField('Reset Password')


class AvatarForm(FlaskForm):
    """
    For uploading new avatars
    """
    file = FileField('Avatar')
    submit = SubmitField('Change Avatar')


class ProductionSearchForm(FlaskForm):
    choices = [('orderNo', 'Order Number'),
               ('productName', 'Product Name'),
               ('serialNo', 'Serial #'),
               ('date', 'Date')]
    select = SelectField('Search for records:', choices=choices, validators=[DataRequired()])
    search = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')
    # noinspection SpellCheckingInspection
    downl = SubmitField('Download!', validators=[Optional()])
    clear = SubmitField('Clear', validators=[Optional()])


class ImportForm(FlaskForm):
    file = FileField('Excel File', validators=[DataRequired()])
    new_sheet_import = SubmitField('New Import', validators=[Optional()])


class SheetDeleteForm(FlaskForm):
    choices = [('sheetName', 'Sheet Name')]
    select = SelectField('Search Term: ', choices=choices)
    search = StringField('')
    submit = SubmitField('Search')


class TemplateDownloadForm(FlaskForm):
    laptop = SubmitField('Laptops')
    desktop_template_download = SubmitField('Desktops')
    processing_template_download = SubmitField('Processing')
    lcd_template_download = SubmitField('LCDs')


class KilldiskForm(FlaskForm):
    choices = [('OrderNo', 'Order Number'),
               ('DiskSerial', 'Serial #'),
               ('Host', 'Drawer')]
    select = SelectField('Search Field:', choices=choices)
    search = StringField('')
    # noinspection SpellCheckingInspection
    startdate = DateField('Start Date', format='%Y-%m-%d', validators=[Optional()])
    # noinspection SpellCheckingInspection
    enddate = DateField('End Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Submit')
    # noinspection SpellCheckingInspection
    downl = SubmitField('Download', validators=[Optional()])
    clear = SubmitField('Clear', validators=[Optional()])


class DateForm(FlaskForm):
    # noinspection SpellCheckingInspection
    startdate = DateField('Start Date', format='%Y-%m-%d')
    # noinspection SpellCheckingInspection
    enddate = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Submit')
    # noinspection SpellCheckingInspection
    downl = SubmitField('Download', validators=[Optional()])
    clear = SubmitField('Clear', validators=[Optional()])


# For inputting HDD validations.
class ValidationEntryForm(FlaskForm):
    # This is a combination of Make and Model
    disk_info = StringField('')
    # Serial # of drive being verified.
    serial = StringField('')
    # Checkbox for whether drive has been successfully sanitized. Required for form submission.
    sanitization = BooleanField(render_kw={'value': 1}, validators=[DataRequired()])
    # Date field for when drive was verified. Required for form submission.
    valid_date = DateField('Validation Date', format='%Y-%m-%d', validators=[DataRequired()])
    # Initials of person verifying drive.
    initials = StringField('')
    # Submit button to submit form.
    submit = SubmitField('Add Record')

# class MasterValidationForm(FlaskForm):


class EquipmentChecklistForm(FlaskForm):
    description = StringField('', validators=[DataRequired()])
    manufacturer = StringField('', validators=[DataRequired()])
    model = StringField('', validators=[DataRequired()])
    yearMFG = StringField('', validators=[DataRequired()])
    countryMFG = StringField('', validators=[DataRequired()])
    serialNo = TextAreaField('', validators=[DataRequired()])
    R2Applicability = RadioField('R2 Applicability', choices=[('C', 'Controlled'), ('U', 'Unrestricted')],
                                 validators=[DataRequired()])
    dataSanitization = RadioField('Data Sanitization', choices=[('D1', 'Pre-Sanitization'), ('D2', 'Non-Data')],
                                  validators=[DataRequired()])
    nextProcess = RadioField('Next Process', choices=[('Test & Repair', 'Test & Repair'), ('Dismantle', 'Dismantle'),
                                                      ('Shred', 'Shred'), ('Commodity Storage', 'Commodity Storage')],
                             validators=[DataRequired()])
    equipmentType = RadioField('Type Of Equipment', choices=[('PC/Laptop', 'PC/Laptop'),
                                                             ('Cellular Phone/Tablet', 'Cellular Phone/Tablet'),
                                                             ('Test/Analytical', 'Test/Analytical'), ('Other', 'Other'),
                                                             ('Components', 'Components'),
                                                             ('LCD/LED Displays', 'LCD/LED Displays'),
                                                             ('Printers', 'Printers'),
                                                             ('New', 'New - No Testing Required'),
                                                             ('Switches/Networking', 'Switches/Networking'),
                                                             ('Office/IP Phone', 'Office/IP Phone'),
                                                             ('A/V Equipment', 'A/V Equipment'),
                                                             ], validators=[DataRequired()])
    otherTypeText = StringField('')
    condition = RadioField('Physical Condition', choices=[('Excellent', 'Excellent - Looks like brand new, no scuffs,'
                                                                        ' no scratches, no dents or dings'),
                                                          ('Very Good', 'Very Good - Minor scuffs or scratches,'
                                                                        ' no dents or dings'),
                                                          ('Good', 'Good - Normal to heavy scuffing and scratching,'
                                                                   ' a few dents or dings'),
                                                          ('Fair', 'Significant scuffing or scratching,'
                                                                   ' several dents or dings'),
                                                          ('Poor', 'Poor - Extreme scuffing or scratching,'
                                                                   ' extreme dents or dings'),
                                                          ], validators=[DataRequired()])
    post = RadioField('Power On Self Test', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')], default='N/A',
                      validators=[DataRequired()])
    chargingBattery = RadioField('AC Adapter Charges Battery', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                                 default='N/A', validators=[DataRequired()])
    batLoadTest = RadioField('Battery Load Test', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                             default='N/A', validators=[DataRequired()])
    batOrgCap = IntegerField('')
    capAtTest = IntegerField('')
    percentOfOrg = IntegerField('')
    keyMouse = RadioField('Keyboard/Mouse Function', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                          default='N/A', validators=[DataRequired()])
    speaker = RadioField('Speaker Functionality', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                         default='N/A', validators=[DataRequired()])
    hinges = RadioField('Hinges, Covers, Clasps', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                        default='N/A', validators=[DataRequired()])
    display = RadioField('LCD/Display', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                         default='N/A', validators=[DataRequired()])
    screenTest = RadioField('Black/White Screen Test', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                            default='N/A', validators=[DataRequired()])
    dataWipe = RadioField('Data Wipe/Sanitize Complete', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                          default='N/A', validators=[DataRequired()])
    crtTest = RadioField('Secure CRT Test', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                                 default='N/A', validators=[DataRequired()])
    internalTest = RadioField('Self/Internal Test', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                              default='N/A', validators=[DataRequired()])
    portTest = RadioField('IP Port Test', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                          default='N/A', validators=[DataRequired()])
    poeTest = RadioField('POE Test', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                         default='N/A', validators=[DataRequired()])
    knobFunction = RadioField('Knob/Button Functionality', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                              default='N/A', validators=[DataRequired()])
    digitizer = RadioField('Digitizer/Display Inspection', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                           default='N/A', validators=[DataRequired()])
    homeScreen = RadioField('POST to Home Screen', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                            default='N/A', validators=[DataRequired()])
    testPage = RadioField('Test Page Print', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                          default='N/A', validators=[DataRequired()])
    otherTest = RadioField('Other', choices=[('Yes', 'Yes'), ('No', 'No'), ('N/A', 'N/A')],
                       default='N/A', validators=[DataRequired()])
    otherTestText = TextAreaField('')
    newOrUsed = RadioField('New/Used', choices=[('New', 'New'), ('Used', 'Used')], validators=[DataRequired()])
    R2Status = RadioField('R2 Status', choices=[('R2 Failed', 'R2 Failed'), ('R2 Passed', 'R2 Passed')],
                          validators=[DataRequired()])
    saleCategory = RadioField('Sale Category',
                              choices=[('Full Function', 'Tested for Full Functions, R2/Ready for Reuse'),
                                       ('Key Function', 'Tested for Key Functions, R2/Ready for Resale'),
                                       ('Non-Functioning', 'Evaluated and Non-Functioning, R2/Ready for Repair'),
                                       ('Collectable/Specialty Equipment', 'Collectable/Specialty Equipment'),
                                        ], validators=[DataRequired()])
    disclosure = TextAreaField('')
    quantity = IntegerField('', validators=[DataRequired()])
    techNotes = TextAreaField('')
    zip = FileField(widget=FileInput(), validators=[FileRequired(), FileAllowed('zip', "Zip Files only!")])
    submit = SubmitField('Complete Record?')


class CustomerSearchForm(FlaskForm):
    bol_number = StringField("")
    customer_name = StringField('')
    submit = SubmitField("Search")


class CustomerEntryForm(FlaskForm):
    customer_name = StringField('')
    submit = SubmitField('Save')


class AikenProductionForm(FlaskForm):
    start_date = DateField('Start Date', [Optional()], format='%Y-%m-%d')
    end_date = DateField('End Date', [Optional()], format='%Y-%m-%d')
    active_lots = BooleanField('Active Lots?')
    graph = SubmitField('Graph')
    table = SubmitField('Table')
    download = SubmitField('Download')







