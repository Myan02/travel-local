import requests
import json
from flask import Blueprint, render_template, jsonify, request, session, url_for
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/')
@login_required
def profile():
    posts = get_user_posts()
    return render_template('profile/profile.html', posts=posts)

def get_user_posts():
    db = get_db()
    all_posts = db.execute(
        'SELECT p.*, u.username'
        ' FROM post p'
        ' JOIN archive a ON p.id = a.post_id'
        ' JOIN user u ON p.author_id = u.id'
        f' WHERE a.user_id = {session["user_id"]}'
        ' ORDER BY created DESC;'
    ).fetchall()
    return all_posts

@bp.route('/search_flights', methods=['POST'])
@login_required
def search_flights():
    if request.method == 'POST':
        # Extract search parameters from the form
        search_number = request.form.get('flight_number')
        search_airline = request.form.get('flight_airline')
        search_status = request.form.get('flight_status')
        search_limit = request.form.get('flight_limit', type=int)

        # Define the base URL and API key
        base_url = 'http://api.aviationstack.com/v1/flights'
        api_key = 'c6006612b5a8a2904527b524c84e59d6'  # Replace with your actual API key

        # Create parameters dictionary with common parameters
        params = {'access_key': api_key}

        # Set the limit parameter if provided, default to 5 if not
        params['limit'] = search_limit if search_limit is not None else 5

        # Check if a specific flight number is provided
        if search_number:
            params['flight_number'] = search_number

        # Check if a specific airline code is provided
        if search_airline:
            params['airline_iata'] = search_airline

        # Check if a specific status is provided
        if search_status:
            params['flight_status'] = search_status

        # Perform the API request with the constructed parameters
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json().get('data', [])
            results = []

            for flight in data:
                destination = flight.get('arrival', {}).get('airport', '')
                departure = flight.get('departure', {}).get('airport', '')
                flight_number = flight.get('flight', {}).get('iata', '')

                result = {
                    'destination': destination,
                    'departure': departure,
                    'flight_number': flight_number
                }

                results.append(result)

            return jsonify(results)
        else:
            # Handle the case when the API request fails
            print('Failed to fetch data from Aviation Stack API')
            return jsonify({'error': 'Failed to fetch data from Aviation Stack API'}), 500

    # Handle the case when the request method is not POST
    return jsonify({'error': 'Invalid request method'}), 400