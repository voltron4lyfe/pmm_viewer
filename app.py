# Import the Flask module
import os
import urllib.parse
import yaml
from flask import render_template
from flask.app import Flask


# Create an instance of the Flask class
app = Flask(__name__)
app_config = yaml.load(open("config.yml", 'r'), Loader=yaml.SafeLoader)
app.config.from_object(app_config)

def generate_overseerr_urls(tmdb_id):
    urls = []
    for overseerr_instance in app_config["overseerr"]:
        urls.append({
            "name" : overseerr_instance["name"],
            "url" : f'{overseerr_instance["url"]}/movie/{urllib.parse.quote(str(tmdb_id))}'
        })
    return urls

def process_tmdbmovielist(movie_list):
    processed_list = []
    for tmdb_id, movie_name in movie_list.items():
        overseerr_urls = generate_overseerr_urls(tmdb_id)
        movie = {
            "tmdb_id" : tmdb_id,
            "name" : movie_name,
            "overseerr_urls" : overseerr_urls,
            "tmdb_url" : f'https://www.themoviedb.org/movie/{tmdb_id}'
        }
        processed_list.append(movie)

    return processed_list

# Define a route and a view function
@app.route('/')
def show_report():
    # Specify the directory path
    directory = './reports'

    report_files = [file for file in os.listdir(directory) if file.endswith('.yml')]
    return render_template('index.html', report_files=report_files)

@app.route('/report/<report_name>')
def show_report_details(report_name):
    file_path = os.path.join('./reports/' + report_name)
    report_file = open(file_path, 'r')
    report = yaml.load(report_file, Loader=yaml.SafeLoader)

    collections = []
    for collection_name, pmm_collection in report.items():
        collection = {
            "name" : collection_name,
            "missing_tmbdbids" : [],
            "added_tmdbids" : [],
            "added" : [],
            "filtered" : []
        }
        collection["missing_tmdbids"] = process_tmdbmovielist(pmm_collection.get('Movies Missing (TMDb IDs)', {}))
        collection["added_tmdbids"] = process_tmdbmovielist(pmm_collection.get('Movies Added (TMDb IDs)', {}))
        #collection["added"] = process_movielist(pmm_collection.get('Movies Added', {}))
        #collection["filtered"]  = process_movielist(pmm_collection.get('Movies Filtered (TMDB IDs)', {})) 
        collections.append(collection)

    return render_template('report_view.html', collections=collections)

@app.route('/report/<report_name>/<collection_name>')
def show_report_details(report_name, collection_name):
    file_path = os.path.join('./reports/' + report_name)
    report_file = open(file_path, 'r')
    report = yaml.load(report_file, Loader=yaml.SafeLoader)

    collections = []
    for collection_name, pmm_collection in report.items():
        collection = {
            "name" : collection_name,
            "missing_tmbdbids" : [],
            "added_tmdbids" : [],
            "added" : [],
            "filtered" : []
        }
        collection["missing_tmdbids"] = process_tmdbmovielist(pmm_collection.get('Movies Missing (TMDb IDs)', {}))
        collection["added_tmdbids"] = process_tmdbmovielist(pmm_collection.get('Movies Added (TMDb IDs)', {}))
        #collection["added"] = process_movielist(pmm_collection.get('Movies Added', {}))
        #collection["filtered"]  = process_movielist(pmm_collection.get('Movies Filtered (TMDB IDs)', {})) 
        collections.append(collection)

    return render_template('report_view.html', collections=collections)
    
# Run the app
if __name__ == '__main__':
    app.run()