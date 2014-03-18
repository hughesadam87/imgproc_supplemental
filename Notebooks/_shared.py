""" Shared utilities to reduce boilerplate between examples.  Stuff like 
importing test images and so one.  Wanted to just be able to import a function
from a  notebook, but this is fairly involved:
http://nbviewer.ipython.org/github/ipython/ipython/blob/master/examples/notebooks/Importing%20Notebooks.ipynb
"""

import os.path as op
import skimage.io as io

def load_test_image(basename, version=1):
    """ Import test image rfrom ../images/Test_Data/Vesrion1"""

    RELPATH =  '../images/Test_Data/Version1'
    if version == 1:
        relpath = op.join(RELPATH, basename)
    else:
        raise AttributeError("Only Version1 Images are available.")
    return io.imread(relpath)

def SEM_test_images(version=1):
    if version != 1:
        raise AttributeError("Only Version1 Images are available.")
    lTi = load_test_image
    names = ['SEM_test_%s.png' % x for x in ('nosmooth', 'smooth', 'noise')]
    return map(load_test_image, names)