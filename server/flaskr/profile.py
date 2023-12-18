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
      search_value = request.get_json().get('search')  # Use get_json() directly
      delimiters = [',', ' ', ':']
      
      for delimiter in delimiters:
         search_value = ' '.join(search_value.split(delimiter))
         
      search_result = search_value.split()
         
      search_dict = {}
      for param in range(0,len(search_result), 2):
         search_dict[search_result[param]] = search_result[param + 1]
        

      # Perform a search query based on the search value
      results = perform_flight_search(search_dict)

      # Return the results as JSON
      return jsonify(results)

def perform_flight_search(search_dict):
    api_key = 'c6006612b5a8a2904527b524c84e59d6'  # Replace with your actual API key
    base_url = 'http://api.aviationstack.com/v1/flights'

    params = {
        'access_key': api_key,
        'limit': search_dict['limit'],
        'flight_number': search_dict['flight'],
        'flight_status': search_dict['status']
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        results = []

        for flight in data.get('data', []):
            destination = flight.get('arrival', {}).get('airport', '')
            departure = flight.get('departure', {}).get('airport', '')
            flight_number = flight.get('flight', {}).get('iata', '')

            result = {
                'destination': destination,
                'departure': departure,
                'flight_number': flight_number
            }

            results.append(result)

        return results
    else:
        # Handle the case when the API request fails
        print('Failed to fetch data from Aviation Stack API')
        return []