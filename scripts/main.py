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
            print(f"Last rating change: {time_gap.days} days ago")
            rating = data['result'][-1]['newRating']
            if time_gap.days > 30:
                rating = 0
            return rating
        else:
            print(data['result'][-1]['handle'])
            print(f"Error: {data.get('comment', 'Unknown error')}")
            return 0
    except Exception as e:
        print(f"Error fetching CF rating for {handle}: {str(e)}")
        return 0

def process_data():
    coders = []
    
    with open(CSV_PATH, 'r') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for row in reader:
            cf_rating = get_codeforces_rating(row['cf'])
            score = cf_rating * 0.8  # Modify this calculation as needed
            
            coders.append({
                'name': row['name'],
                'cf_handle': row['cf'],
                'cf_rating': cf_rating,
                'cc_handle': row.get('cc', ''),
                'rating': score
            })
            row_count += 1
            # if row_count >= 5: break
    
    coders.sort(key=lambda x: x['rating'], reverse=True)
    
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