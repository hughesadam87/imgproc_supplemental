""" Shared utilities to reduce boilerplate between examples.  Stuff like 
importing test images and so one.  Wanted to just be able to import a function
from a  notebook, but this is fairly involved:
http://nbviewer.ipython.org/github/ipython/ipython/blob/master/examples/notebooks/Importing%20Notebooks.ipynb
"""

import os.path as op
import skimage.io as io
import pyparty.utils as putls
from functools import partial

IMGDIR = '../images'

def load_test_image(basename, relpath = 'Test_Data/Version1', crop=None):
    """ Import test image relative to ../images/relpath"""

    fullrelpath = op.join(IMGDIR, relpath)
    path = op.join(fullrelpath, basename)
    img = io.imread(path)
    if crop:
        cropper = partial(putls.crop, coords=crop)
        img = cropper(img)
    return img

def SEM_test_images(crop=None):
    lTi = load_test_image
    names = ['SEM_test_%s.png' % x for x in ('nosmooth', 'smooth', 'noise')]
    return [load_test_image(n, crop=crop) for n in names]
