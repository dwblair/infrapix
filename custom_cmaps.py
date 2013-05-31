import numpy as np
import matplotlib
 
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
