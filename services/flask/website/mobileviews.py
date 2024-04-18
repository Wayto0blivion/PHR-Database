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

    return render_template('skeleton_mobile_weight_sheet.html', boxes=boxes, user=current_user)













