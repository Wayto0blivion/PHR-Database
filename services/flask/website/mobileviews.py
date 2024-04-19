from . import db, sqlEngine, app, qrcode
from .forms import MobileDeviceForm, MobileClosingForm, MobileNewWeightForm
from .models import Mobile_Weights, Mobile_Pallets, Mobile_Boxes, Mobile_Box_Devices
from datetime import datetime
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
    # Query Mobile_Boxes table for all boxes associated with a given pallet id
    boxes = Mobile_Boxes.query.filter_by(palletID=pallet_id).order_by(Mobile_Boxes.box_number).all()

    # Ensure there are always 24 boxes by appending dummy boxes. This should be irrelevant.
    while len(boxes) < 24:
        boxes.append(Mobile_Boxes(is_active=False))

    return render_template('skeleton_mobile_box_list.html', boxes=boxes, user=current_user)


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
    # Empty dictionary variable to store information needed to display
    data = {}

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

    if device_form.validate_on_submit():  # What to do if user tries to add a device to the box
        pass

    if close_form.validate_on_submit():  # What to do if the user tries to close box or pallet
        pass

    # DEBUG
    devices = [[device.model, str(device.weight)] for device in devices]

    return render_template('skeleton_mobile_weight_sheet.html', device_form=device_form,
                           close_form=close_form, data=data, user=current_user)




