#!flask/bin/python
from flask import render_template, flash, redirect, session, url_for, \
        request, g, send_file, abort, jsonify

from flask_login import current_user
from flask_qrcode import QRcode

from app import app, db, lm
from datetime import datetime, timedelta
from config import STREAMLABS_CLIENT_ID, STREAMLABS_CLIENT_SECRET, \
        CASHTIP_REDIRECT_URI

from .forms import RegisterForm, ProfileForm
from .models import User, PayReq, Transaction

from pycoin.key import Key
from pycoin.key.validate import is_address_valid
from exchanges.bitstamp import Bitstamp
from exchanges.bch_bittrex import bch_price
from decimal import Decimal
from .payment import check_payment_on_address, check_address_history
import pprint
import json
import bitcoin
import requests
import time
import sys
import qrcode
import os
from werkzeug.datastructures import ImmutableOrderedMultiDict

streamlabs_api_url = 'https://www.streamlabs.com/api/v1.0/'
api_token = streamlabs_api_url + 'token'
api_user = streamlabs_api_url + 'user'
api_tips = streamlabs_api_url + "donations"
api_custom = streamlabs_api_url + "alerts"
callback_result = 0

@app.route('/_verify_payment', methods=['POST'])
def verify_payment():
    btc_addr = request.form['btc_addr']
    social_id = request.form['social_id']
    db.session.commit()
    payrec_check = PayReq.query.filter_by(addr=btc_addr).first()

    print("PAYMENT CHECK")
    history_check = check_address_history(btc_addr)
    payment_check_return = {
            'transaction_found': None,
            'payment_verified' : "FALSE",
            'user_display'     : User.query.filter_by(
                social_id=social_id
                ).first().nickname
    }
    print("***" + "checking for history on: " + btc_addr + "***\n")
    if history_check and payrec_check:
        payment_check_return['payment_verified'] = "TRUE"
        print("Payment Found!")
        amount = check_payment_on_address(btc_addr)
        print(amount)
        payment_check_return['transaction_found'] = history_check[0]['tx_hash']

        payment_notify(social_id,
                payrec_check,
                amount,
                history_check[0]['tx_hash'],
                btc_addr)

        db.session.delete(payrec_check)
        db.session.commit()
    return jsonify(payment_check_return)

def payment_notify(social_id, payrec, balance, txhash, grs_addr):
    '''
    Exchange Rate json file contains:
    'exchange' : BitStamp/BitFinex/Kraken/Etc
    'rate'     : USD-Pair Exchange Rate for BTC
    'datetime' : timestamp of when last grabbed
    '''
    user = User.query.filter_by(social_id=social_id).first()
    print(balance)
    value = balance * bch_price()
    is_latest_exchange_valid = False

    # if exchangerate.json doesnt already exists, create a new one
    if not os.path.exists('exchangerate.json'):
        f = open('exchangerate.json', 'w')
        f.write("{}")
        f.close()

    with open("exchangerate.json", 'r') as f:
        latestexchange = json.loads(f.read())
        # if the file is valid ('datetime' key exists), go on and parse it
        if 'datetime' in latestexchange:
            latestexchange['datetime'] = datetime.strptime(
                latestexchange['datetime'], '%Y-%m-%d %H:%M:%S.%f')

            if (datetime.today() - latestexchange['datetime']) <= timedelta(hours=1):
                print("using existing exchange rate")
                is_latest_exchange_valid = True
                exchange = latestexchange['rate']

    # If we fail to get exchange rate from Bitstamp,
    # use old, stored value.
    print("Exchange rate too old! Grabbing exchange rate from Bitstamp")
    try:
        exchange = Bitstamp().get_current_price()
        latestexchange = {
                'exchange' : 'bitstamp',
                'rate'     : float(exchange),
                'datetime' : str(datetime.today())
                }

        print("exchage rate data found!")
        print(latestexchange)
        with open('exchangerate.json', 'w') as f:
            print("Opened exchange rate file for recording")
            json.dump(latestexchange, f)
        print("exchange rate recorded")
    except:
        if is_latest_exchange_valid:
            exchange = latestexchange['rate']
        else:
            exchange = Bitstamp().get_current_price()

    usd_value = ((value) * float(exchange)/100000000)
    usd_two_places = float(format(usd_value, '.2f'))
    grs_amount = ((balance) /100000000)
    #print(usd_two_places)
    token_call = {
                    'grant_type'    : 'refresh_token',
                    'client_id'     : STREAMLABS_CLIENT_ID,
                    'client_secret' : STREAMLABS_CLIENT_SECRET,
                    'refresh_token' : user.streamlabs_rtoken,
                    'redirect_uri'  : CASHTIP_REDIRECT_URI
    }
    headers = []
    #print("Acquiring Streamlabs Access Tokens")
    tip_response = requests.post(
            api_token,
            data=token_call,
            headers=headers
    ).json()
    #print("Tokens Acquired, Committing to Database")

    user.streamlabs_rtoken = tip_response['refresh_token']
    user.streamlabs_atoken = tip_response['access_token']
    db.session.commit()

    grs_amount_display = " ("+ str('%g' % grs_amount) +" BCH Donated)"

    if payrec.user_message:
        msg=payrec.user_message

    else:
        msg=''

    tip_call = {
            'name'       : payrec.user_display,
            'identifier' : payrec.user_identifier,
            'message'    : msg+grs_amount_display,
            'amount'     : usd_two_places,
            'currency'   : 'USD',
            'access_token' : tip_response['access_token'],
            'skip_alert' : 'yes'
    }
    tip_check = requests.post(
            api_tips,
            data=tip_call,
            headers=headers
        ).json()
    donation = "*" + payrec.user_display +"* donated *$" + str(usd_two_places) + "* in BCH!\n"
    tip_call = {
            'type'       : 'donation',
            'message'    : donation,
            'user_message' : msg,
            'image_href' : user.image_ref,
            'sound_href' : user.sound_ref,
            'duration'   : 5000,
            'special_text_color' : user.text_color,
            'access_token' : tip_response['access_token']
    }
    print(tip_call)

    min_amount = str(user.min_donation_ref)
    print(min_amount)
    if min_amount == 'None':
        tip_check_alert = requests.post(api_custom, data=tip_call, headers=headers).json()
        print(tip_check_alert)
    else:
        min_amount_float = float(user.min_donation_ref)
        if usd_two_places >= min_amount_float:
            tip_check_alert = requests.post(api_custom, data=tip_call, headers=headers).json()
            print(tip_check_alert)

    # custom_notify(social_id, payrec.user_message, value, usd_two_places)
    print("Saving transaction data in database...")
    # transaction = Transaction.query.filter_by(addr=btc_addr).first()
    payreq = PayReq.query.filter_by(addr=grs_addr).first()
    new_transaction = Transaction(
        twi_user=payreq.user_display,
        twi_message=payreq.user_message,
        user_id=social_id,
        tx_id=txhash,
        amount=str('%g' % grs_amount),
        timestamp=payreq.timestamp
        )
    db.session.add(new_transaction)
    db.session.commit()

    print("Transaction data saved!")
    print("Donation Alert Sent")


    return tip_check

@app.route('/_create_payreq', methods=['POST'])
def create_payment_request():
    social_id = request.form['social_id']
    deriv = User.query.filter_by(social_id = social_id).first(). \
            latest_derivation
    address = get_unused_address(social_id, deriv)
    new_payment_request = PayReq(
            address,
            user_display=request.form['user_display'],
            user_identifier=request.form['user_identifier']+"_grs",
            user_message=request.form['user_message']
            )
    db.session.add(new_payment_request)
    db.session.commit()
    return jsonify(
            {'btc_addr': address}
            )

@app.route('/tip/<username>')
def tip(username):
    u = User.query.filter_by(social_id=username.lower()).first()
    if u:
        try:
            session_nickname = session['nickname']

        except:

            session_nickname = None

        dono_str = u.min_donation_ref
        return render_template('tipv2.html', session_nickname=session_nickname, nickname = u.nickname, social_id = u.social_id, display_text = u.display_text, email = u.paypal_email, dono = u.min_donation_ref)
    else:
        return render_template(

            '404.html',
            username=username
            )

def get_unused_address(social_id, deriv):
    '''
    Need to be careful about when to move up the latest_derivation listing.
    Figure only incrementing the database entry when blockchain activity is
    found is the least likely to create large gaps of empty addresses in
    someone's BTC Wallet.
    '''
    pp = pprint.PrettyPrinter(indent=2)
    userdata = User.query.filter_by(social_id = social_id).first()

    # Pull BTC Address from given user data
    key = Key.from_text(userdata.xpub).subkey(0). \
            subkey(deriv)

    address = key.address(use_uncompressed=False)

    # Check for existing payment request, delete if older than 5m.
    payment_request = PayReq.query.filter_by(addr=address).first()
    if payment_request:
        req_timestamp = payment_request.timestamp
        now_timestamp = datetime.utcnow()
        delta_timestamp = now_timestamp - req_timestamp
        if delta_timestamp > timedelta(seconds=60*5):
            db.session.delete(payment_request)
            db.session.commit()
            payment_request = None

    if not check_address_history(address):
        if not payment_request:
            return address
        else:
            print("Address has payment request...")
            print("Address Derivation: ", deriv)
            return get_unused_address(social_id, deriv + 1)
    else:
        print("Address has blockchain history, searching new address...")
        print("Address Derivation: ", userdata.latest_derivation)
        userdata.latest_derivation = userdata.latest_derivation + 1
        db.session.commit()
        return get_unused_address(social_id, deriv + 1)
