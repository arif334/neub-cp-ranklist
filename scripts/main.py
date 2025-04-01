import csv
import json
import requests
from datetime import datetime
import os

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
            print(f"Last rating change of {handle}: {time_gap.days} days ago")
            rating_actual = data['result'][-1]['newRating']
            rating = rating_actual
            if time_gap.days > 30:
                rating = 0
            return rating, rating_actual
        else:
            print(data['result'][-1]['handle'])
            print(f"Error: {data.get('comment', 'Unknown error')}")
            return [0, 0]
    except Exception as e:
        print(f"Error fetching CF rating for {handle}: {str(e)}")
        return [0, 0]

def process_data():
    coders = []
    
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for row in reader:
            cf_rating, cf_rating_actual = get_codeforces_rating(row['cf'])
            score = cf_rating * 0.8  # Modify this calculation as needed

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
            
            coders.append({
                'id': id,
                'name': row['name'],
                'cf_handle': row['cf'],
                'cf_color': cf_color,
                'cc_handle': row.get('cc', ''),
                'atcoder_handle': row.get('atcoder', ''),
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