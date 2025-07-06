import csv
import json
import requests
from datetime import datetime, timezone
import os
from dateutil import parser

CSV_PATH = 'data/coder-info.csv'
OUTPUT_JSON = 'docs/assets/data.json'

def get_codeforces_rating(handle):
    try:
        response = requests.get(f'https://codeforces.com/api/user.rating?handle={handle}')
        data = response.json()
        # print(data)
        if response.status_code == 200:
            lastChange = data['result'][-1]['ratingUpdateTimeSeconds']
            time_gap = datetime.now() - datetime.fromtimestamp(lastChange)
            # print(f"Last rating change of {handle}: {time_gap.days} days ago")
            rating_actual = data['result'][-1]['newRating']
            rating = rating_actual
            if time_gap.days > 30:
                rating = 0
            return rating, rating_actual
        else:
            # print(data['result'][-1]['handle'])
            # print(f"Error: {data.get('comment', 'Unknown error')}")
            return [0, 0]
    except Exception as e:
        # print(f"Error fetching CF rating for {handle}: {str(e)}")
        return [0, 0]

def get_atcoder_rating(handle):
    try:
        response = requests.get(f'https://atcoder.jp/users/{handle}/history/json')
        if response.status_code == 200:
            data = response.json()
            # Filter contests to include only rated contests
            rated_contests = [contest for contest in data if contest.get('IsRated', False)]
            if rated_contests:  # Check if there are any rated contests
                last_rated_contest = rated_contests[-1]  # Get the most recent rated contest
                # Parse EndTime and convert to Unix timestamp
                last_change = parser.isoparse(last_rated_contest['EndTime']).timestamp()
                time_gap = datetime.now().timestamp() - last_change
                days_gap = time_gap // 86400  # Convert seconds to days
                # print(f"Last AtCoder contest of {handle}: {int(days_gap)} days ago")
                rating_actual = last_rated_contest['NewRating']
                rating = rating_actual
                if days_gap > 30:
                    rating = 0
                return rating, rating_actual
            else:
                # print(f"No rated ATC contest history found for {handle}")
                return [0, 0]
        else:
            # print(f"Error fetching AtCoder rating for {handle}: {response.status_code}")
            return [0, 0]
    except Exception as e:
        # print(f"Exception: Error fetching AtCoder rating for {handle}: {str(e)}")
        return [0, 0]
    

def get_codechef_rating(handle):
    if not handle or handle.strip() == '':
        return [0, 0]  # Return early if handle is empty
    
    try:
        response = requests.get(f'https://codechef-api.vercel.app/handle/{handle}', timeout=20)
        if response.status_code == 200:
            data = response.json()
            if 'ratingData' in data and len(data['ratingData']) > 0:
                # Get the most recent rating data
                last_rating_data = data['ratingData'][-1]
                rating_actual = int(last_rating_data.get('rating', 0))
                
                # Parse end_date to calculate days since last contest
                if 'end_date' in last_rating_data:
                    end_date = last_rating_data['end_date']
                    # Parse date in format "2025-04-02 22:00:00"
                    last_change = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").timestamp()
                    time_gap = datetime.now().timestamp() - last_change
                    days_gap = time_gap // 86400  # Convert seconds to days
                    print(f"Last CodeChef contest of {handle}: {int(days_gap)} days ago")
                    
                    # Apply similar decay rule as AtCoder
                    rating = rating_actual
                    if days_gap > 30:
                        rating = 0
                    return rating, rating_actual
                else:
                    # If no end_date, assume it's current
                    rating = rating_actual
                    return rating, rating_actual
            else:
                print(f"No rating found for CodeChef handle: {handle}")
                return [0, 0]
        else:
            print(f"Error fetching CodeChef rating for {handle}: {response.status_code}")
            return [0, 0]
    except Exception as e:
        print(f"Exception: Error fetching CodeChef rating for {handle}: {str(e)}")
        return [0, 0]

def get_codechef_rating_neub(handle):
    """
    Fetch CodeChef rating info from the NEUB CodeChef API.
    API: https://neub-codechef-api.vercel.app/{handle}
    Returns [rating, rating_actual] similar to get_codechef_rating.
    ** API Developped by: Nayef
    """
    if not handle or handle.strip() == '':
        return [0, 0]  # Return early if handle is empty

    try:
        response = requests.get(f'https://neub-codechef-api.vercel.app/api/rating/{handle}', timeout=10)
        if response.status_code == 200:
            info = response.json()
            # The API returns a dict with 'rating' and 'lastUpdated' keys
            rating_actual = int(info.get('data', {}).get('rating', 0))
            last_contest = info.get('data', {}).get('lastContestDate', None)
            # print(last_contest)
            if last_contest:
                # last_contest is expected in "YYYY-MM-DD" format
                last_change = parser.isoparse(last_contest).timestamp()
                time_gap = datetime.now(timezone.utc).timestamp() - last_change
                # print(f"time_gap: {time_gap}")
                days_gap = time_gap // 86400  # Convert seconds to days
                print(f"Last CodeChef contest of {handle}: {int(days_gap)} days ago")
                rating = rating_actual
                if days_gap > 30:
                    rating = 0
                return rating, rating_actual
            else:
                # If no last_contest, assume it's current
                return rating_actual, rating_actual
        else:
            print(f"Error fetching CodeChef rating (NEUB API) for {handle}: {response.status_code}")
            return [0, 0]
    except Exception as e:
        print(f"Exception: Error fetching CodeChef rating (NEUB API) for {handle}: {str(e)}")
        return [0, 0]

def process_data():
    coders = []
    
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for row in reader:
            score = float(row['offline'])

            # Processing CodeForces ratings
            cf_rating, cf_rating_actual = get_codeforces_rating(row['cf'])
            cf_score = (cf_rating * 50) / 1500
            score += cf_score

            id = row['id']
            if id.startswith('56'): 
                id = '0' + id

            cf_color = 'gray'
            if cf_rating_actual >= 2400: cf_color = 'red'
            elif cf_rating_actual >= 2100: cf_color = 'orange'
            elif cf_rating_actual >= 1900: cf_color = 'purple'
            elif cf_rating_actual >= 1600: cf_color = 'blue'
            elif cf_rating_actual >= 1400: cf_color = 'cyan'
            elif cf_rating_actual >= 1200: cf_color = 'green'
            
            # Processing AtCoder ratings
            atc_rating, atc_rating_actual = get_atcoder_rating(row['atcoder'])
            atc_score = (atc_rating * 30) / 1300
            score += atc_score

            atc_color = 'gray'  # Default color for unrated users
            if atc_rating_actual >= 2800: 
                atc_color = '#FF0000'  # Red
            elif atc_rating_actual >= 2400: 
                atc_color = '#FF8000'  # Orange
            elif atc_rating_actual >= 2000: 
                atc_color = '#C0C000'  # Yellow
            elif atc_rating_actual >= 1600: 
                atc_color = '#0000FF'  # Blue
            elif atc_rating_actual >= 1200: 
                atc_color = '#00C0C0'  # Cyan
            elif atc_rating_actual >= 800: 
                atc_color = '#008000'  # Green
            elif atc_rating_actual >= 400: 
                atc_color = '#804000'  # Brown

            # Processing CodeChef ratings
            # cc_rating, cc_rating_actual = get_codechef_rating(row['cc'])
            cc_rating, cc_rating_actual = get_codechef_rating_neub(row['cc'])
            cc_score = (cc_rating * 30) / 1600
            score += cc_score # score += cc_score -> uncomment this after experiment

            cc_color = 'gray'
            if cc_rating_actual >= 2200: cc_color = 'red'
            elif cc_rating_actual >= 2000: cc_color = 'orange'
            elif cc_rating_actual >= 1800: cc_color = 'cyan'
            elif cc_rating_actual >= 1600: cc_color = 'blue'
            elif cc_rating_actual >= 1400: cc_color = 'green'

            coders.append({
                'id': id,
                'name': row['name'],
                'cf_handle': row['cf'],
                'cf_color': cf_color,
                'cc_handle': row.get('cc', ''),
                'cc_color': cc_color,
                'atcoder_handle': row.get('atcoder', ''),
                'atc_color': atc_color,
                'score': score
            })
            row_count += 1
            # if row_count >= 5: break
    
    coders.sort(key=lambda x: x['score'], reverse=True)
    
    output = {
        'meta': {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_coders': len(coders)
        },
        'data': coders
    }
    
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(output, f, indent=2)

if __name__ == '__main__':
    # print(os.getcwd())
    process_data()