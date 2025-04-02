import csv
import json
import requests
from datetime import datetime
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
                print(f"Last AtCoder contest of {handle}: {int(days_gap)} days ago")
                rating_actual = last_rated_contest['NewRating']
                rating = rating_actual
                if days_gap > 30:
                    rating = 0
                return rating, rating_actual
            else:
                print(f"No rated ATC contest history found for {handle}")
                return [0, 0]
        else:
            print(f"Error fetching AtCoder rating for {handle}: {response.status_code}")
            return [0, 0]
    except Exception as e:
        print(f"Exception: Error fetching AtCoder rating for {handle}: {str(e)}")
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

            atc_color = 'gray'
            if atc_rating_actual > 2800: atc_color = 'red'
            elif atc_rating_actual > 2400: atc_color = 'orange'
            elif atc_rating_actual > 2000: atc_color = 'yellow'
            elif atc_rating_actual > 1600: atc_color = 'blue'
            elif atc_rating_actual > 1000: atc_color = 'lightblue'
            elif atc_rating_actual > 800: atc_color = 'green'
            elif atc_rating_actual > 400: atc_color = 'brown'

            coders.append({
                'id': id,
                'name': row['name'],
                'cf_handle': row['cf'],
                'cf_color': cf_color,
                'cc_handle': row.get('cc', ''),
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