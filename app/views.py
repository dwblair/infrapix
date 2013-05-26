from app import app
import os
from flask import Flask, render_template, send_from_directory, send_file, request, url_for, jsonify, redirect, Request

import flask_sijax

from cStringIO import StringIO
from werkzeug import secure_filename

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
#import numpy
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

from PIL import Image

# uploading parameters

#UPLOAD_FOLDER = '/home/asine/infrapix.pvos.org/app/uploads'
#NDVI_FOLDER = '/home/asine/infrapix.pvos.org/app/ndvi'

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
NDVI_FOLDER = os.path.join(app.root_path, 'ndvi')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['NDVI_FOLDER'] = NDVI_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


#sijax stuff
path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')

app = Flask(__name__)
app.config['SIJAX_STATIC_PATH'] = path
app.config['SIJAX_JSON_URI'] = '/static/js/sijax/json2.js'
flask_sijax.Sijax(app)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')


def nir(imageInPath,imageOutPath):
    img = mpimg.imread(imageInPath)
    red=img[:,:,0]
    arrR=np.asarray(red).astype('float64')
   
    arr_nir=arrR

    fig=plt.figure()
    fig.set_frameon(False)
    ax=fig.add_subplot(111)
    ax.set_axis_off()
    ax.patch.set_alpha(0.0)

    nir_plot = ax.imshow(arr_nir, cmap=plt.cm.gist_gray, interpolation="nearest")

    #fig.colorbar(nir_plot)
    fig.savefig(imageOutPath)

 
def ndvi(imageInPath,imageOutPath):
    #img1 = Image.open(imageInPath) 
    img = mpimg.imread(imageInPath)
    red=img[:,:,0]
    green=img[:,:,1]
    blue=img[:,:,2]

    arrR=np.asarray(red).astype('float64')
    arrG=np.asarray(green).astype('float64')
    arrB=np.asarray(blue).astype('float64')
    num=arrR - arrB
    num=(arrR - arrB)
    denom=(arrR + arrB)
    arr_ndvi=num/denom
    
    fig=plt.figure()
    fig.set_frameon(False)
    ax=fig.add_subplot(111)
    ax.set_axis_off()
    ax.patch.set_alpha(0.0)

    ndvi_plot = ax.imshow(arr_ndvi, cmap=plt.cm.spectral, interpolation="nearest")
    fig.colorbar(ndvi_plot)
    fig.savefig(imageOutPath)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method=='POST':
        file=request.files['file']
        if file: 
            filename=file.filename
            uploadFilePath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
            file.save(uploadFilePath)
            ndviFilePath=os.path.join(app.config['UPLOAD_FOLDER'],'ndvi_'+filename)
            nirFilePath=os.path.join(app.config['UPLOAD_FOLDER'],'nir_'+filename)
            ndvi(uploadFilePath,ndviFilePath)
            nir(uploadFilePath,nirFilePath)
            return redirect(url_for('uploaded_file',filename=filename)) 
    return '''
        <!doctype html>
        <img src="http://i.publiclab.org/system/images/photos/000/000/264/medium/main-image-med.jpg"><br>
        <title>Infragram Online!</title>
<br>
Welcome to Public Lab's online service for generating NDVI from near-infrared pictures!</br><br>

        <h2>Upload new file</h2>

To upload a file for processing, please click on the "Choose File" button below.  After you've selected a file, click "Upload".

        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
                 <input type=submit value=Upload>
        </form>
        '''

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)


@app.route('/show/<filename>')
def uploaded_file(filename):
    uploadFilePath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
    ndviFilePath=os.path.join(app.config['NDVI_FOLDER'],filename)  
    return render_template('template.html',filename='/uploads/'+filename, ndviFilename='/uploads/'+'ndvi_'+filename, nirFilename='/uploads/'+'nir_'+filename)

