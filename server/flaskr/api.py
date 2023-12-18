import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db
from flaskr.auth import login_required

import requests
from flask_cors import cross_origin

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/home')
def api_home():
    if request.method == 'GET':
        print(f'\n\ni made it this far\n\n')
        return render_template('api/home.html')

@bp.route('get', methods=['POST'])
@cross_origin()
def api():
    if request.method == 'POST':
        api_key = '1a419b5c83877f83023bb96ea8608c41'
        flight_number = '135'
        
        if not flight_number:
            return jsonify({'error': 'Flight number is required'}), 400

        base_url = 'https://api.aviationstack.com/v1/flights?access_key=1a419b5c83877f83023bb96ea8608c41&flight_number=135'
        params = {
            'access_key': api_key,
            'flight_number': flight_number
        }

        response = requests.get(base_url)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify(data)
        else:
            return jsonify({'error': 'Failed to fetch data from Aviation Stack API'}), 500

    # Handle GET requests if needed
    return jsonify({'error': 'Only POST requests are allowed for this endpoint'}), 400
    
    
