import requests
import json
from flask import Blueprint, render_template, jsonify, request, session, url_for
from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('profile', __name__, url_prefix='/profile')

# show archived posts
@bp.route('/')
@login_required
def profile():
    posts = get_user_posts()
    return render_template('profile/profile.html', posts=posts)

# retrieve archived posts
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

# search api for flights 
@bp.route('/search_flights', methods=['POST'])
@login_required
def search_flights():
    if request.method == 'POST':
        # get search bar values
        search_number = request.form.get('flight_number')
        search_airline = request.form.get('flight_airline')
        search_status = request.form.get('flight_status')
        search_limit = request.form.get('flight_limit', type=int)

        # set the url and api key
        base_url = 'http://api.aviationstack.com/v1/flights'
        api_key = 'c6006612b5a8a2904527b524c84e59d6'

        params = {'access_key': api_key}

        # Set the base limit to show 5 results, but can be overwritten
        params['limit'] = search_limit if search_limit is not None else 5

        # check if specific fields are provided or empty
        if search_number:
            params['flight_number'] = search_number

        if search_airline:
            params['airline_iata'] = search_airline

        if search_status:
            params['flight_status'] = search_status

        # create master link
        response = requests.get(base_url, params=params)

        # check for good response
        if response.status_code == 200:
            data = response.json().get('data', [])
            results = []

            # set data to output
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
            # handle case if api request is bad
            print('Failed to fetch data from Aviation Stack API')
            return jsonify({'error': 'Failed to fetch data from Aviation Stack API'}), 500

    # handle case if someone tries to access the route as a GET request
    return jsonify({'error': 'Invalid request method'}), 400