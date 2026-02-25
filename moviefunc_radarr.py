import dotenv
import os
import json
import time
import requests
import yaml

dotenv.load_dotenv()

RADARR_URL = os.getenv('RADARR_URL')
RADARR_API_KEY = os.getenv('RADARR_API_KEY')
YAML_OUTPUT_FOLDER = "/srv/scripts/radarr"

def arr_request(path: str, method="GET", **kwargs):
    url = f'{RADARR_URL}{path}'
    headers = {'accept': 'application/json', 'X-Api-Key': RADARR_API_KEY}
    if method == "POST":
        response = requests.post(url, headers=headers, **kwargs)
    elif method == "PUT":
        response = requests.put(url, headers=headers, **kwargs)
    else:
        response = requests.get(url, headers=headers, **kwargs)
    return response.json()

def query_queue(filepath: str, dest_slug: str) -> None:
    """
    Create a YAML file in the output folder with the movie's Id qualityProfileId and a constructured destination path
    Query the API for the movie based on filepath
    YAML Output Example:
    id: 689
    qualityProfileId: 1
    path: "/mnt/data/Movies/Movie (2014)"
    """
    # Replace the filepath because of Radarr path
    # Only used when in the scratch folder
    radarr_path = filepath.replace('/mnt/nvme/share/scratch','/ssd/scratch')
    movies = arr_request('/api/v3/movie')
    movie = next((movie for movie in movies if movie['path'] == radarr_path), None)
    if movie is None:
        print(f"Movie not found for path: {radarr_path}")
        time.sleep(3) # for SpaceFM to not exit
        return
    output = {
        'id': movie['id'],
        'qualityProfileId': movie['qualityProfileId'],
        'path': f"/{dest_slug}/Movies/{os.path.basename(filepath).rsplit('.', 1)[0]}"
    }
    with open(os.path.join(YAML_OUTPUT_FOLDER, f"{movie['id']}.yaml"), 'w') as yaml_file:
        yaml.dump(output, yaml_file)
