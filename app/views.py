
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from app import app
import os
from flask import Flask, render_template, send_from_directory, send_file, request, url_for, jsonify, redirect, Request, g

from cStringIO import StringIO
from werkzeug import secure_filename

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
#import numpy
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as numpy

from PIL import Image

import flask_sijax

#UPLOAD_FOLDER = '/home/asine/infrapix.pvos.org/app/uploads'
#NDVI_FOLDER = '/home/asine/infrapix.pvos.org/app/ndvi'

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
NDVI_FOLDER = os.path.join(app.root_path, 'ndvi')


#UPLOAD_FOLDER = '/home/asine/infrapix.pvos.org/public/uploads'
#NDVI_FOLDER = '/home/asine/infrapix.pvos.org/public/ndvi'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['NDVI_FOLDER'] = NDVI_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


# sijax stuff
path = os.path.join(app.root_path, 'static/js/sijax/')
app.config['SIJAX_STATIC_PATH']= path
app.config['SIJAX_JSON_URI']='/static/js/sijax/json2.js'
flask_sijax.Sijax(app)


#@app.route('/')
#@app.route('/index')
#def index():
#    return "Hello, World!"

# Regular flask view function - Sijax is unavailable here
@app.route("/sijaxTest")
def hello():
    return "Hello World!<br /><a href='/sijax'>Go to Sijax test</a>"

# Sijax enabled function - notice the `@Sijax.route` decorator
# used instead of `@app.route` (above).
@flask_sijax.route(app, "/sijax")
def hello_sijax():
    # Sijax handler function receiving 2 arguments from the browser
    # The first argument (obj_response) is passed automatically
    # by Sijax (much like Python passes `self` to object methods)
    def hello_handler(obj_response, hello_from, hello_to):
        obj_response.alert('Hello from %s to %s' % (hello_from, hello_to))
        obj_response.css('a', 'color', 'green')

    # Another Sijax handler function which receives no arguments
    def goodbye_handler(obj_response):
        obj_response.alert('Goodbye, whoever you are.')
        obj_response.css('a', 'color', 'red')

    if g.sijax.is_sijax_request:
        # The request looks like a valid Sijax request
        # Let's register the handlers and tell Sijax to process it
        g.sijax.register_callback('say_hello', hello_handler)
        g.sijax.register_callback('say_goodbye', goodbye_handler)
        return g.sijax.process_request()

    return render_template('hello.html')




@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

### generating ndvi

def nir(imageInPath,imageOutPath):
    img = mpimg.imread(imageInPath)
    red=img[:,:,0]
    arrR=numpy.asarray(red).astype('float64')
   
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
	img=Image.open(imageInPath)
	imgR, imgG, imgB = img.split() #get channels
	arrR = numpy.asarray(imgR).astype('float64')
	arrB = numpy.asarray(imgB).astype('float64')
	"""img = mpimg.imread(imageInPath)
	red=img[:,:,0]
	green=img[:,:,1]
	blue=img[:,:,2]

	arrR=np.asarray(red).astype('float64')
	arrG=np.asarray(green).astype('float64')
	arrB=np.asarray(blue).astype('float64')
	"""
	num=arrR - arrB
	num=(arrR - arrB)
	denom=(arrR + arrB)
	arr_ndvi=num/denom

	## adding higher-res code
	AUTO_CONTRAST = False
	img_w, img_h = img.size
	dpi   = 600#int(img_w/fig_w)
	vmin  = -1.0 #most negative NDVI value
	vmax  =  1.0 #most positive NDVI value
	if AUTO_CONTRAST:
		vmin = arr_ndvi.min()
		vmax = arr_ndvi.max() 

	fig_w = img_w/dpi
	fig_h = img_h/dpi
	fig = plt.figure(figsize=(fig_w,fig_h), dpi=dpi)
	fig.set_frameon(False)

	#make an axis for the image filling the whole figure except colorbar space
	ax_rect = [0.0, #left
           0.0, #bottom
           1.0, #width
           1.0] #height
	ax = fig.add_axes(ax_rect)
	ax.yaxis.set_ticklabels([])
	ax.xaxis.set_ticklabels([])   
	ax.set_axis_off()
	ax.patch.set_alpha(0.0)

	axes_img = ax.imshow(arr_ndvi,
			              cmap = plt.cm.spectral, 
			              vmin = vmin,
			              vmax = vmax,
			              aspect = 'equal',
			              #interpolation="nearest"
			             )
	# Add colorbar
	#make an axis for colorbar
	cax = fig.add_axes([0.95,
			            0.05,
			            0.025,
			            0.90]
			           ) #fill the whole figure
	cbar = fig.colorbar(axes_img, cax=cax)  #this resizes the axis

	#fig.tight_layout(pad=0)
	fig.savefig(imageOutPath, 
			    dpi=dpi,
			    bbox_inches='tight',
			    pad_inches=0.0, 
			   )
	

"""
	#fig=plt.figure()
	#fig.set_frameon(False)
	ax=fig.add_subplot(111)
	ax.set_axis_off()
	ax.patch.set_alpha(0.0)

	#custom_cmap=make_cmap_gaussianHSV(bandwidth=0.01,num_segs=1024)
	ndvi_plot = ax.imshow(arr_ndvi, cmap=plt.cm.spectral, interpolation="nearest")
	#ndvi_plot = ax.imshow(arr_ndvi, cmap=custom_cmap, interpolation="nearest")

	fig.colorbar(ndvi_plot)
	fig.savefig(imageOutPath)
"""

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
<head>
<title>infrapix!</title>
<link type="text/css" rel="stylesheet" href="{{ url_for('static', filename='css/bootstrap/css/bootstrap.css') }}" />
<link type="text/css" rel="stylesheet" href="{{ url_for('static', filename='css/slider.css') }}" />
</head>
<body class="container">


        <img src="http://i.publiclab.org/system/images/photos/000/000/264/medium/main-image-med.jpg"><br>
        <title>Infragram Online!</title>
<br>
Welcome to Public Lab's online service for generating NDVI from near-infrared pictures!</br><br>

<div class="well">
        <h2>Upload a new file</h2>

To upload a file for processing, please click on the "Choose File" button below.  After you've selected a file, click "Upload".

        <form action="" method=post enctype=multipart/form-data>
          <p><input type=file name=file>
                 <input type=submit value=Upload>
        </form>
</div>
</body>
</html>

        '''

@app.route('/uploads/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)


@app.route('/show/<filename>')
def uploaded_file(filename):
    uploadFilePath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
    ndviFilePath=os.path.join(app.config['NDVI_FOLDER'],filename)  
    return render_template('sliders.html',filename='/uploads/'+filename, ndviFilename='/uploads/'+'ndvi_'+filename, nirFilename='/uploads/'+'nir_'+filename)




###### sijax uploader ######

class SijaxHandler(object):
    """A container class for all Sijax handlers.

    Grouping all Sijax handler functions in a class
    (or a Python module) allows them all to be registered with
    a single line of code.
    """

    @staticmethod
    def _dump_data(obj_response, files, form_values, container_id):
        def dump_files():
            if 'file' not in files:
                return 'Bad upload'

            file_data = files['file']
            file_name = file_data.filename
            if file_name is None:
                return 'Nothing uploaded'

            file_type = file_data.content_type
            file_size = len(file_data.read())
            return 'Uploaded file %s (%s) - %sB' % (file_name, file_type, file_size)

        html = """Form values: %s<hr />Files: %s"""
        html = html % (str(form_values), dump_files())

        obj_response.html('#%s' % container_id, html)

    @staticmethod
    def form_one_handler(obj_response, files, form_values):
        SijaxHandler._dump_data(obj_response, files, form_values, 'formOneResponse')

    @staticmethod
    def form_two_handler(obj_response, files, form_values):
        SijaxHandler._dump_data(obj_response, files, form_values, 'formTwoResponse')

        obj_response.reset_form()
        obj_response.html_append('#formTwoResponse', '<br />Form elements were reset!<br />Doing some more work (2 seconds)..')

        # Send the data to the browser now
        yield obj_response

        from time import sleep
        sleep(2)

        obj_response.html_append('#formTwoResponse', '<br />Finished!')


@flask_sijax.route(app, "/sijaxUploadTest")
def index():
    # Notice how we're doing callback registration on each request,
    # instead of only when needed (when the request is a Sijax request).
    # This is because `register_upload_callback` returns some javascript
    # that prepares the form on the page.
    form_init_js = ''
    form_init_js += g.sijax.register_upload_callback('formOne', SijaxHandler.form_one_handler)
    form_init_js += g.sijax.register_upload_callback('formTwo', SijaxHandler.form_two_handler)

    if g.sijax.is_sijax_request:
        # The request looks like a valid Sijax request
        # The handlers are already registered above.. we can process the request
        return g.sijax.process_request()

    return render_template('upload.html', form_init_js=form_init_js)

############# sijax comet test ################

def comet_do_work_handler(obj_response, sleep_time):
    import time

    for i in range(6):
        width = '%spx' % (i * 80)
        obj_response.css('#progress', 'width', width)
        obj_response.html('#progress', width)

        # Yielding tells Sijax to flush the data to the browser.
        # This only works for Streaming functions (Comet or Upload)
        # and would not work for normal Sijax functions
        yield obj_response

        if i != 5:
            time.sleep(sleep_time)


@flask_sijax.route(app, "/sijaxCometTest")
def index():
    if g.sijax.is_sijax_request:
        # The request looks like a valid Sijax request
        # Let's register the handlers and tell Sijax to process it
        g.sijax.register_comet_callback('do_work', comet_do_work_handler)
        return g.sijax.process_request()

    return render_template('comet.html')

##### testing out twitter bootstrap

@app.route("/slidertest")
def index():
    return render_template('sliders.html')

