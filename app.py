import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from google.cloud import vision
import re
import shutil
import predict  # Import predict.py for the prediction functionality
import pprint
from gcloud import storage
from services import ImagesAdaptor
from datetime import datetime

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}
app.config['RESULT_FOLDER'] = 'static/results'
app.config['GOOGLE_APPLICATION_CREDENTIALS'] = r'key.json'

vision_client = vision.ImageAnnotatorClient()

@app.route('/vision.html', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file:
                image_filename = file.filename
                image_content = file.read()
                image = vision.Image(content=image_content)
                response = vision_client.text_detection(image=image)
                texts = response.text_annotations
                extracted_text = extract_date_and_weight(" ".join(text.description for text in texts))

                # Save a copy of the uploaded image to the 'static/uploads' directory with the original filename
                upload_folder = os.path.join('static', 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                image_path = os.path.join(upload_folder, image_filename)
                with open(image_path, 'wb') as image_file:
                    image_file.write(image_content)

                return redirect(url_for('result', image_url=image_filename, extracted_text=extracted_text))

    return render_template('vision.html', extracted_text=None)  # Pass extracted_text to the template

@app.route('/vision.html', methods=['GET'])
def result():
    image_url = request.args.get('image_url')
    extracted_text = request.args.get('extracted_text')

    return render_template('vision.html', image_url=image_url, extracted_text=extracted_text)

def extract_date_and_weight(text):
    date_pattern = r'\b\d{1,2}/\d{1,2}/\d{2,4}\b'
    weight_pattern = r'WEIGHT\s*:\s*(\d+\.\d+)\b'

    date_match = re.search(date_pattern, text)
    weight_match = re.search(weight_pattern, text)

    date = date_match.group(0) if date_match else "Date not found"
    weight = weight_match.group(1) if weight_match else "Weight not found"

    return f"Date: {date}, Weight: {weight}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/coral.html', methods=['GET', 'POST'])
def upload_and_run_inference():
    original_images = []
    result_images = []

    if request.method == 'POST':
        if 'files' not in request.files:
            return "Geen bestand geselecteerd."

        files = request.files.getlist('files')

        for file in files:
            if file.filename == '':
                return "Geen bestandsnaam opgegeven."

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                result_image_names = predict.run_inference(file_path, app.config['RESULT_FOLDER'])

                upload_to_database(app.config['GOOGLE_APPLICATION_CREDENTIALS'], os.path.join(app.config['RESULT_FOLDER'], filename), os.path.join(app.config['UPLOAD_FOLDER'], filename))

                if result_image_names:
                    original_images.append(filename)
                    result_images.extend(result_image_names)
                else:
                    return 'Resultaatmap niet gevonden.'
            else:
                return 'Ongeldig bestandsformaat. Toegestane formaten zijn: .jpg, .jpeg, .png, .gif'

    return render_template('coral.html', original_images=original_images, result_images=result_images)

def upload_to_database(service_account_key, image_path, original_image_path):
    # Authorize project and select bucket
    client = storage.Client.from_service_account_json(service_account_key)
    bucket = client.get_bucket('sumthing_images')  

    service = ImagesAdaptor("http://127.0.0.1:5000")

    blob = bucket.blob(image_path)
    blob.upload_from_filename(image_path)

    blob_original = bucket.blob(original_image_path)
    blob_original.upload_from_filename(original_image_path)

    image = {
                "bucket": get_blob_URI(blob),
                "bucket_original": get_blob_URI(blob_original),
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "longitude": 0,
                "latitude": 0
            }
            
    service.save_image(image)

def get_blob_URI(blob):
    """Prints out and returns a blob's gsutil_URI"""

    # Source: https://stackoverflow.com/a/76093697
    gsutil_URI = 'gs://' + blob.id[:-(len(str(blob.generation)) + 1)]
    pprint.pprint = "gsutil URI: " + gsutil_URI
    return gsutil_URI

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/results/<result_image_name>')
def show_result(result_image_name):
    return render_template('result.html', result_image_name=result_image_name)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
