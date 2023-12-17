import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flaskr.auth import login_required

import requests

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/home')
def api_home():
    if request.method == 'GET':
        print(f'\n\ni made it this far\n\n')
        return render_template('api/home.html')


@bp.route('/get', methods=['GET', 'POST'])
def api():
    api_key = '657d604030bad43384fcb694'
    # base_url = f'https://partners.api.skyscanner.net/apiservices/v3/'
    base_url = 'https://api.flightapi.io/onewaytrip/657d604030bad43384fcb694/HEL/OUL/2024-05-20/1/0/0/Economy/USD'

    
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')

    # Update these values with your specific market, currency, and locale
    market = 'US'
    currency = 'USD'
    locale = 'en-US'

    # Construct the API request URL
    api_url = f"{base_url}{market}/{currency}/{locale}/{origin}/{destination}/{date}?query=fran&apiKey={api_key}"

    response = requests.get(base_url)
   
    if response.status_code == 200:
      data = response.json()
      return jsonify(data)
    else:
        return jsonify({'error': 'Failed to fetch data from Skyscanner API'}), 500
    
    
