from . import db, sqlEngine, app, qrcode
from .forms import MobileDeviceForm, MobileClosingForm, MobileNewWeightForm, ImportForm
from .models import Mobile_Weights, Mobile_Pallets, Mobile_Boxes, Mobile_Box_Devices
from datetime import datetime
from decimal import Decimal
from flask import Flask, Blueprint, render_template, render_template_string, request, session, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import website.helper_functions as hf
import numpy as np
import pandas as pd


# noinspection SpellCheckingInspection
mobileviews = Blueprint('mobileviews', __name__)

# TODO: Add closing timestamp to boxes and pallets to track both when opened and closed.
# TODO: Update user when pallet or box are closed.


@mobileviews.route('/', methods=['GET', 'POST'])
@login_required
def mobile_home():
    """
    Starts a new pallet and opens boxes for it if no active pallet.
    Redirects user to view_pallet_boxes with the active pallet id
    """
    # Check for an active pallet.
    pallet = Mobile_Pallets.query.filter_by(is_active=True).first()

    if not pallet:  # Create a new pallet if an active one wasn't detected
        print('Creating new pallet.')
        new_pallet = Mobile_Pallets(is_active=True, user=current_user.id)
        db.session.add(new_pallet)
        db.session.commit()

        # Create boxes 1-24 tied to the newly created pallet.
        for box in range(1, 25):
            print(f'Creating new box! {box}')
            new_box = Mobile_Boxes(is_active=True, box_number=box, palletID=new_pallet.autoID, user=current_user.id)
            db.session.add(new_box)
            db.session.commit()

        # Set the active pallet to the newly created pallet.
        pallet = new_pallet

    return redirect(url_for('mobileviews.mobile_pallet', pallet_id=pallet.autoID, user=current_user))


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

    # Ensure there are always 24 boxes by appending dummy boxes. This should be irrelevant.
    while len(boxes) < 24:
        boxes.append(Mobile_Boxes(is_active=False))

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
        return redirect(url_for('mobileviews.mobile_home', user=current_user))

    return render_template('skeleton_mobile_box_list.html', boxes=boxes,
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
    data['closed_box_count'] = Mobile_Boxes.query.filter_by(palletID=data['palletID'], is_active=False).count()

    # Get a list of devices in the current box, joined with the model and weight.
    devices = (db.session.query(Mobile_Box_Devices, Mobile_Weights.model, Mobile_Weights.weight)
               .join(Mobile_Weights, Mobile_Weights.autoID == Mobile_Box_Devices.modelID)
               .filter(Mobile_Box_Devices.boxID == box_id)
               .all())
    # Add basic device info to data dictionary
    data['devices'] = [[device.model, device.weight, device[0].qty] for device in devices]

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
            db.session.add(new_weight)
            db.session.commit()
            # Add the new model to the current box.
            new_device = Mobile_Box_Devices(boxID=box_id, modelID=new_weight.autoID,
                                            qty=session.get('device_qty'), user=current_user.id)
            db.session.add(new_device)
            db.session.commit()

            # Clear session variables now that they have been used.
            session.pop('device_model')
            session.pop('device_qty')
            return redirect(url_for('mobileviews.mobile_box', box_id=box_id, user=current_user))

    if device_form.validate_on_submit():  # What to do if user tries to add a device to the box
        if device_form.add_button.data:
            # Check if the model exists in the Mobile_Weights table.
            check_model = Mobile_Weights.query.filter_by(model=device_form.model.data).first()
            # If not, send the user to enter a new model.
            if not check_model:
                print(f'Model not found: {device_form.model.data}')
                data['show_weight_form'] = True
                # Adds data from device form to session so that weight form can access it.
                session['device_model'] = device_form.model.data.upper()
                session['device_qty'] = device_form.quantity.data
                return render_template('skeleton_mobile_weight_sheet.html', data=data, user=current_user)
            # If the model was found, add it to the box.
            else:
                print(f"The model found was {check_model.autoID}")
                # Check if the selected model already exists in the current box.
                current_model = Mobile_Box_Devices.query.filter_by(modelID=check_model.autoID, boxID=box_id).first()
                if not current_model:  # IF the model doesn't already exist in the current box, add it.
                    new_device = Mobile_Box_Devices(boxID=box_id, modelID=check_model.autoID, qty=device_form.quantity.data,
                                                    user=current_user.id)
                    db.session.add(new_device)
                else:  # If the model already exists, increase the quantity.
                    current_model.qty += device_form.quantity.data

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



