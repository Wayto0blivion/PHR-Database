from . import db, sqlEngine, app, qrcode
from .forms import (MobileDeviceForm, MobileClosingForm, MobileNewWeightForm, MobileBoxSearchForm,
                    MobileBoxModificationForm, MobileWeightAdminSearchForm, ImportForm, MobileAdminAddWeightForm)
from .models import Mobile_Weights, Mobile_Pallets, Mobile_Boxes, Mobile_Box_Devices, User
from datetime import datetime
from decimal import Decimal
from flask import (Flask, Blueprint, render_template, render_template_string, request, session, redirect, url_for,
                   flash, jsonify, send_file, make_response)
from flask_login import login_required, current_user
import website.helper_functions as hf
import numpy as np
import pandas as pd


# noinspection SpellCheckingInspection
mobileviews = Blueprint('mobileviews', __name__)

# The total number of boxes to generate per pallet.
total_boxes = 27

# TODO: Add closing timestamp to boxes and pallets to track both when opened and closed.
# TODO: Update user when pallet or box are closed.


@mobileviews.route('/', methods=['GET', 'POST'])
@login_required
def mobile_home():
    """
    Starts a new pallet and opens boxes for it if no active pallet.
    Redirects user to view_pallet_boxes with the active pallet id
    """

    # Check if the current user has admin permissions for this page, and if so,
    # forward them to the "all_pallets" page.
    # TODO: Update the permission once the new one (permission set) is created.
    if current_user.admin_status:
        return redirect(url_for('mobileviews.all_open_pallets'))

    # Check for an active pallet for the current user.
    pallet = Mobile_Pallets.query.filter_by(is_active=True, user=current_user.id).first()

    if not pallet:  # Create a new pallet if an active one wasn't detected
        print('Creating new pallet.')
        new_pallet = Mobile_Pallets(is_active=True, user=current_user.id)
        db.session.add(new_pallet)
        db.session.commit()

        # Create boxes 1-24 tied to the newly created pallet.
        for box in range(1, total_boxes + 1):
            print(f'Creating new box! {box}')
            new_box = Mobile_Boxes(is_active=True, box_number=box, palletID=new_pallet.autoID, user=current_user.id)
            db.session.add(new_box)
            db.session.commit()

        # Set the active pallet to the newly created pallet.
        pallet = new_pallet

    return redirect(url_for('mobileviews.mobile_pallet', pallet_id=pallet.autoID, user=current_user))


@mobileviews.route("/all_pallets", methods=["GET", "POST"])
@login_required
def all_open_pallets():
    """
    Designed to show all open pallets and the user assigned to them.
    Lets the user select which pallet they want to view.
    """
    # Get a dictionary of all open pallets with their respective users to display to admins
    open_pallets = Mobile_Pallets.query.filter_by(is_active=True).all()
    pallet_list = {}
    # Return a list of pallet ids from the open pallets.
    for open_pallet in open_pallets:
        user = User.query.filter_by(id=open_pallet.user).first().first_name
        pallet_list[user] = open_pallet.autoID

    return render_template('skeleton_mobile_all_pallets.html', pallet_list=pallet_list, user=current_user)


@mobileviews.route('/pallet/<int:pallet_id>', methods=['GET', 'POST'])
@login_required
def mobile_pallet(pallet_id):
    """
    Show the available boxes from the currently active pallet in a 6x4 grid.
    """
    # Create an instance of the closed form.
    close_form = MobileClosingForm()
    # Query Mobile_Boxes table for all boxes associated with a given pallet id
    boxes = Mobile_Boxes.query.filter_by(palletID=pallet_id).order_by(Mobile_Boxes.box_number).all()

    # Ensure there are always total_boxes number of boxes by appending dummy boxes. This should be irrelevant.
    while len(boxes) < total_boxes:
        boxes.append(Mobile_Boxes(is_active=False))

    # Create a dictionary for all weights of open boxes
    weights = {}
    for box in boxes:
        devices = (db.session.query(Mobile_Box_Devices, Mobile_Weights.model, Mobile_Weights.weight)
                   .join(Mobile_Weights, Mobile_Weights.autoID == Mobile_Box_Devices.modelID)
                   .filter(Mobile_Box_Devices.boxID == box.autoID)
                   .all())
        total_box_weight = Decimal(0.0)
        good_count = 0
        bad_count = 0
        for device in devices:
            total_box_weight += (device.weight * device[0].qty)
            if device[0].good_device:
                good_count += 1
            else:
                bad_count += 1
        weights[box.box_number] = [total_box_weight, good_count, bad_count]
        # print(weights[box.box_number])

    # Handle the closing of the pallet and all boxes tied to it.
    if close_form.validate_on_submit():
        print('Validating Close Form')
        # Handle closing all boxes tied to the pallet first.
        for box in boxes:
            if box.is_active:
                box.is_active = False
        db.session.commit()
        # Handle closing the pallet itself.
        current_pallet = Mobile_Pallets.query.filter_by(autoID=pallet_id).first()
        current_pallet.is_active = False
        db.session.commit()
        # Reload the page so the user starts a new pallet.
        return mobile_pallet_export(pallet_id=pallet_id)

    return render_template('skeleton_mobile_box_list.html', boxes=boxes, weights=weights,
                           close_form=close_form, user=current_user)


@mobileviews.route('/box/<int:box_id>', methods=['GET', 'POST'])
@login_required
def mobile_box(box_id):
    """
    Displays the current contents of the box.
    Allows user to add new devices to a box.
    """
    # Get references to the two forms needed to read from.
    device_form = MobileDeviceForm()
    close_form = MobileClosingForm()
    # Get a reference to the Weight Form
    weight_form = MobileNewWeightForm()
    # Store forms in a dictionary to store data passed to HTML
    data = {'device_form': device_form, 'close_form': close_form, 'weight_form': weight_form,
            'show_weight_form': False}

    # Get the current pallet by finding it based on box_id
    pallet = Mobile_Pallets.query.filter_by(autoID=Mobile_Boxes.query.filter_by(autoID=box_id).first().palletID).first()

    # Get data points from pallet to display to user.
    data['palletID'] = pallet.autoID
    data['timestamp'] = pallet.timestamp
    data['current_box_status'] = Mobile_Boxes.query.filter_by(autoID=box_id).first().is_active
    data['closed_box_count'] = Mobile_Boxes.query.filter_by(palletID=data['palletID'], is_active=False).count()

    # Get a list of devices in the current box, joined with the model and weight.
    devices = (db.session.query(Mobile_Box_Devices, Mobile_Weights.model, Mobile_Weights.weight)
               .join(Mobile_Weights, Mobile_Weights.autoID == Mobile_Box_Devices.modelID)
               .filter(Mobile_Box_Devices.boxID == box_id)
               .order_by(Mobile_Box_Devices.timestamp.desc())
               .all())
    # Add basic device info to data dictionary
    data['devices'] = [[device.model, device.weight, device[0].qty, device[0].good_device] for device in devices]

    # Calculate the total weight for the current box and add it to data.
    total_box_weight = Decimal(0.0)
    for device in data['devices']:
        total_box_weight += (device[1] * device[2])
    data['total_box_weight'] = total_box_weight

    if weight_form.validate_on_submit():
        if weight_form.submit.data:
            # Convert weight from lbs to kg
            weight_kg = weight_form.weight.data * Decimal(0.453592)
            # Create the new weight object
            new_weight = Mobile_Weights(model=session.get('device_model'), weight=weight_kg,
                                        user=current_user.id)
            print(f'New Weight: {session.get("device_model")} - {new_weight.weight}')
            # Add and submit the new object
            # db.session.add(new_weight)
            # db.session.commit()
            # Add the new model to the current box.
            new_device = Mobile_Box_Devices(boxID=box_id, modelID=new_weight.autoID,
                                            qty=session.get('device_qty'), user=current_user.id)
            # db.session.add(new_device)
            # db.session.commit()

            # Clear session variables now that they have been used.
            session.pop('device_model')
            session.pop('device_qty')
            return redirect(url_for('mobileviews.mobile_box', box_id=box_id, user=current_user))

    if device_form.validate_on_submit():  # What to do if user tries to add a device to the box
        status = None
        # Check if the good button has been pressed, and set the status variable to match.
        if device_form.good_button.data:
            status = True
        if device_form.bad_button.data:
            status = False

        # Make sure one of the two buttons have been pressed.
        if device_form.good_button.data or device_form.bad_button.data:

            # Check if the model exists in the Mobile_Weights table.
            check_model = Mobile_Weights.query.filter_by(model=device_form.model.data).first()
            # If not, send the user to enter a new model.
            if not check_model:
                flash(f'Model not found: {device_form.model.data}', category='error')
                data['show_weight_form'] = True
                # Adds data from device form to session so that weight form can access it.
                session['device_model'] = device_form.model.data.upper()
                session['device_qty'] = device_form.quantity.data
                return render_template('skeleton_mobile_weight_sheet.html', data=data, user=current_user)
            # If the model was found, add it to the box.
            else:
                # flash(f"The model found was {check_model.autoID}", category='success')
                # Check if the selected model already exists in the current box.
                current_model = Mobile_Box_Devices.query.filter_by(modelID=check_model.autoID, boxID=box_id,
                                                                   good_device=status).first()
                if not current_model:  # IF the model doesn't already exist in the current box, add it.
                    new_device = Mobile_Box_Devices(boxID=box_id, modelID=check_model.autoID,
                                                    qty=device_form.quantity.data, user=current_user.id,
                                                    good_device=status)
                    db.session.add(new_device)
                else:  # If the model already exists, increase the quantity.
                    current_model.qty += device_form.quantity.data
                    current_model.timestamp = datetime.now()
                    if current_model.qty == 0:
                        db.session.delete(current_model)
                    # flash(f'Removed {current_model.model}', category='success')

                db.session.commit()
                return redirect(url_for('mobileviews.mobile_box', box_id=box_id, user=current_user))

    if close_form.validate_on_submit():  # What to do if the user tries to close box or pallet
        if close_form.close_box_button.data:
            print('Close Form Box Validated')
            # Set the is_active property of the current box to False.
            current_box = Mobile_Boxes.query.filter_by(autoID=box_id).first()
            current_box.is_active = False
            db.session.commit()
            return redirect(url_for('mobileviews.mobile_home', box_id=box_id, user=current_user))

    return render_template('skeleton_mobile_weight_sheet.html', data=data, user=current_user)


@mobileviews.route('/import', methods=['GET', 'POST'])
def mobile_import():
    """
    Imports a list of models and weights into the Mobile_Weights table from an excel list.
    """
    form = ImportForm()

    if form.validate_on_submit():
        try:
            file = form.file.data
            df = pd.read_excel(file, header=0)

            for index, row in df.iterrows():
                new_weight = Mobile_Weights(model=row['Model'].upper(), weight=row['Weight'], user=current_user.id)
                db.session.add(new_weight)
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f'Error! : {str(e)}')

    return render_template('skeleton_import_weights.html', form=form, user=current_user)


@mobileviews.route('/export/<pallet_id>', methods=['GET', 'POST'])
def mobile_pallet_export(pallet_id=None):
    """
    Exports a list of models and weights into an Excel spreadsheet.
    palletID : The pallet ID to export
    """
    # If no pallet ID was provided, return a jsonify message with an error.
    if pallet_id is None:
        return jsonify({'error': 'No pallet ID'})

    # Get a list of boxes in the pallet_id parameter.
    boxes = Mobile_Boxes.query.filter_by(palletID=pallet_id).order_by(Mobile_Boxes.box_number).all()

    df = pd.DataFrame(columns=['Box', 'Item', 'Battery Weight', 'Quantity', 'Status', 'Total Battery Weight'])

    # Get all devices in each box.
    for box in boxes:
        devices = (db.session.query(Mobile_Box_Devices, Mobile_Weights.model, Mobile_Weights.weight)
                   .join(Mobile_Weights, Mobile_Weights.autoID == Mobile_Box_Devices.modelID)
                   .filter(Mobile_Box_Devices.boxID == box.autoID)
                   .all())

        for device, model, weight in devices:
            device_data = {
                "Box": box.box_number,
                "Item": model,
                "Battery Weight": weight,
                "Quantity": device.qty,
                "Status": 'Good' if device.good_device else 'Bad',
                "Total Battery Weight": weight * device.qty
            }
            df = df.append(device_data, ignore_index=True)

    resp = make_response(df.to_csv(index=False))
    resp.headers['Content-Type'] = 'text/csv'
    resp.headers['Content-Disposition'] = 'attachment; filename=Mobile_Export.csv'
    return resp

    # file_path = 'Mobile_Export.csv'
    # df.to_csv(file_path, index=False)

    # return send_file(file_path, as_attachment=True, download_name="Mobile_Export.csv", mimetype='text/csv')

    # df.to_excel('Mobile_Export.xlsx', index=False)

    # return jsonify({"message": "Export successful"})


@mobileviews.route('/modify-qty', methods=['GET', 'POST'])
def modify_qty():
    """
    Allow modification of entries in the Mobile_Boxes table, handling Auto-ID's as necessary.
    """
    forms = {
        'quantity_form': MobileBoxModificationForm(),
        "search_form": MobileBoxSearchForm()
    }
    # Get a reference to the currently active pallet.
    pallet = Mobile_Pallets.query.filter_by(is_active=True).first()

    if forms["quantity_form"].validate_on_submit():
        # Handle modifying quantities first if this form is active.
        box = session.get('box_number')
        model = session.get('model_number')

        qty = forms["quantity_form"].quantity.data

        entry = Mobile_Box_Devices.query.filter_by(boxID=box, modelID=model).first()

        if qty <= 0:
            db.session.delete(entry)
        elif qty:
            entry.qty = qty

        db.session.commit()

        session.pop('box_number')
        session.pop('model_number')

    if forms["search_form"].validate_on_submit():
        # Get references to the data submitted by user.
        box_search = forms["search_form"].box.data
        model_search = forms["search_form"].model.data

        # Find the corresponding entries for both box and model. Get their autoIDs.
        box_number = Mobile_Boxes.query.filter_by(palletID=pallet.autoID, box_number=box_search).first().autoID
        model_number = Mobile_Weights.query.filter_by(model=model_search).first().autoID
        session["box_number"] = box_number
        session["model_number"] = model_number
        data = {
            "box": box_number,
            "model": model_number,
            "qty": Mobile_Box_Devices.query.filter_by(boxID=box_number, modelID=model_number).first().qty
        }

        return render_template("skeleton_mobile_edits.html", forms=forms, data=data, user=current_user)

    return render_template("skeleton_mobile_edits.html", forms=forms, user=current_user)


@mobileviews.route("/search_weights", methods=['GET', 'POST'])
@login_required
@hf.user_permissions("Admin")
def search_weights():
    """
    Allows an admin to search for an existing master weight and choose one to its value.
    Returns:

    """
    form = MobileWeightAdminSearchForm()

    if form.validate_on_submit():
        if form.submit.data:  # Step One: Search for a model matching the user string.
            matching_models = None
            matching_models = Mobile_Weights.query.filter(Mobile_Weights.model.contains(form.model.data)).all()

            return render_template("skeleton_admin_search_weights.html", form=form,
                                   matching_models=matching_models, user=current_user)
        # Check if a 'Choose Model' button was clicked. Value will be in POST data.
        chose_model_id = request.form.get("choose_model")
        if chose_model_id:
            print(chose_model_id)
            return redirect(url_for("mobileviews.modify_weight", model=chose_model_id, user=current_user))

    return render_template("skeleton_admin_search_weights.html", form=form, user=current_user)


@mobileviews.route("/modify_weight/<model>", methods=['GET', 'POST'])
@login_required
@hf.user_permissions("Admin")
def modify_weight(model):
    """
    Modify the weight of a specific model passed in.
    Args:
        model: The autoID of the model to modify.
    Returns:

    """
    model_info= {}
    form = MobileNewWeightForm()

    db_entry = Mobile_Weights.query.filter_by(autoID=model).first()

    if db_entry:
        model_info["id"] = db_entry.autoID
        model_info["model"] = db_entry.model
        model_info["weight"] = db_entry.weight

    if form.validate_on_submit():
        try:
            db_entry.weight = form.weight.data / Decimal(2.2)
            db.session.commit()
            return redirect(url_for("mobileviews.search_weights", user=current_user))
        except Exception as e:
            db.session.rollback()

    return render_template("skeleton_admin_modify_weight.html", model_info=model_info, form=form,  user=current_user)


@mobileviews.route("/create_weight", methods=['GET', 'POST'])
@login_required
@hf.user_permissions("Admin")
def create_weight():
    """
    Allows the user to create a new master weight.
    Returns:

    """
    form = MobileAdminAddWeightForm()

    if form.validate_on_submit():
        try:
            new_weight = Mobile_Weights()
            new_weight.model = form.model.data
            new_weight.weight = form.weight.data / Decimal(2.2)
            new_weight.user = current_user.id
            db.session.add(new_weight)
            db.session.commit()
            print("Weight Added!")
            flash("Weight Added!")
        except Exception as e:
            print("Rolling back create_weight")
            print(e)
            db.session.rollback()
            flash("Couldn't add weight!")
    else:
        print(form.errors)

    return render_template("skeleton_admin_new_weight.html", user=current_user, form=form)












