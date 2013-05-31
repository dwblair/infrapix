################################################################################
# this is code to compute NDVI from Blue (Visible channel) and Red (Infrared)
# such as pictures taken with "SuperBlue" camera
from PIL import Image
import numpy

img = Image.open("chris.png")
imgR, imgG, imgB = img.split() #get channels
#convert to double precision floating point..is this overkill? probably, could try 'float32' or 'float16'
arrR = numpy.asarray(imgR).astype('float64')
arrB = numpy.asarray(imgB).astype('float64')
num = (arrR - arrB)
denom = (arrR + arrB)
arr_ndvi = num/denom

################################################################################
#the following is only for testing, a better colormapping scheme should be developed
import matplotlib
from matplotlib import pyplot as plt
from custom_cmaps import make_cmap_guassianHSV

AUTO_CONTRAST = False

custom_cmap = make_cmap_guassianHSV(bandwidth=0.1, num_segs=256)

img_w, img_h = img.size

dpi   = 600#int(img_w/fig_w)
vmin  = -1.0 #most negative NDVI value
vmax  =  1.0 #most positive NDVI value
if AUTO_CONTRAST:
   vmin = arr_ndvi.min()
   vmax = arr_ndvi.max() 

#lay out the plot, making room for a colorbar space
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
                      cmap = custom_cmap, 
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
fig.savefig("cmaps-test/IMG_0512_NDVI_%s.JPG" % custom_cmap.name, 
            dpi=dpi,
            bbox_inches='tight',
            pad_inches=0.0, 
           )
