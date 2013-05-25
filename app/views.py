from app import app
import os
from flask import Flask, render_template, send_from_directory, send_file, request, url_for, jsonify, redirect, Request

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

UPLOAD_FOLDER = '/home/asine/infrapix.pvos.org/app/uploads'
NDVI_FOLDER = '/home/asine/infrapix.pvos.org/app/ndvi'

#UPLOAD_FOLDER = '/home/asine/infrapix.pvos.org/public/uploads'
#NDVI_FOLDER = '/home/asine/infrapix.pvos.org/public/ndvi'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['NDVI_FOLDER'] = NDVI_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

#@app.route('/')
#@app.route('/index')
#def index():
#    return "Hello, World!"

@app.route('/woah')
def yabber():
    return "no no no!"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

### generating ndvi

def make_cmap_guassianHSV( num_segs     = 100, #number of segments
                           bandwidth    = 0.25,
                           red_center   = 1.00,
                           green_center = 0.75,
                           blue_center  = 0.50,
                           name = "gaussianHSV"
                         ):
    #this is the color index
    X = np.linspace(0.0,1.0,num_segs)

    Y_R  = np.exp(-(X - red_center  )**2/bandwidth**2)
    Y_G  = np.exp(-(X - green_center)**2/bandwidth**2)
    Y_B  = np.exp(-(X - blue_center )**2/bandwidth**2)

    segs_R = np.vstack((X,Y_R,Y_R)).transpose()
    segs_G = np.vstack((X,Y_G,Y_G)).transpose()
    segs_B = np.vstack((X,Y_B,Y_B)).transpose()
    ##make colormap
    cdict = {
    'red'  :  segs_R,
    'green':  segs_G,
    'blue' :  segs_B,
    }

    cmap = matplotlib.colors.LinearSegmentedColormap(name,cdict,num_segs)
    return cmap



def infr(imageInPath,imageOutPath):
    img = mpimg.imread(imageInPath)
    red=img[:,:,0]

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

    #custom_cmap=make_cmap_gaussianHSV(bandwidth=0.01,num_segs=1024)
    ndvi_plot = ax.imshow(arr_ndvi, cmap=plt.cm.spectral, interpolation="nearest")
    #ndvi_plot = ax.imshow(arr_ndvi, cmap=custom_cmap, interpolation="nearest")

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
            ndvi(uploadFilePath,ndviFilePath)
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
    return render_template('template.html',filename='/uploads/'+filename, ndviFilename='/uploads/'+'ndvi_'+filename)


