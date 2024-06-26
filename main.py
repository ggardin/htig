import os
from flask import Flask, flash, request, redirect, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
import cv2
import numpy as np

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1000 * 1000

# init instance directory
os.makedirs(os.path.join(app.instance_path), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.instance_path, filename))
            edit_image(os.path.join(app.instance_path, filename))
            return redirect(url_for('download_file', filename=filename))
    return render_template('index.html')

@app.route('/uploads/<filename>')
def download_file(filename):
    return send_from_directory(
        app.instance_path, filename
    )

def edit_image(filename):
	# Caricare l'immagine
	immagine_originale = cv2.imread(filename)

	# Definire le nuove dimensioni
	nuova_larghezza = 1080
	nuova_altezza = 1080

	# Calcolare il rapporto di ridimensionamento
	rapporto_ridimensionamento = min(nuova_larghezza / immagine_originale.shape[0], nuova_altezza / immagine_originale.shape[1])

	# Calcolare le dimensioni ridimensionate
	dimensione_ridimensionata = (int(immagine_originale.shape[1] * rapporto_ridimensionamento), int(immagine_originale.shape[0] * rapporto_ridimensionamento))

	# Ridimensionare l'immagine
	immagine_ridimensionata = cv2.resize(immagine_originale, dimensione_ridimensionata, cv2.INTER_AREA)

	# Creare uno sfondo bianco
	sfondo_bianco = np.ones((nuova_altezza, nuova_larghezza, 3), dtype=np.uint8) * 255

	# Posizionare l'immagine ridimensionata al centro dello sfondo
	centro_x = int((nuova_larghezza - dimensione_ridimensionata[0]) / 2)
	centro_y = int((nuova_altezza - dimensione_ridimensionata[1]) / 2)

	sfondo_bianco[centro_y:centro_y + dimensione_ridimensionata[1], centro_x:centro_x + dimensione_ridimensionata[0]] = immagine_ridimensionata

	# Salvare l'immagine modificata
	cv2.imwrite(os.path.join(app.instance_path, filename), sfondo_bianco)

def cleanup():
    for file in os.listdir(app.instance_path):
        os.remove(os.path.join(app.instance_path, file))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

