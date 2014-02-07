# Author:  Adam Hughes
# Created: 12/9/2013
# Email: hugadams@gwmail.gwu.edu


""" Scikit image (skimage) utilities shared by example notebooks."""

from __future__ import division

from skimage import img_as_float, exposure
from skimage.io import imshow
from skimage.color import label2rgb, rgb2hsv, hsv2rgb
from numpy import dstack

import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow
from scipy import ndimage


class UtilsError(Exception):
    pass


def plot_img_and_hist(img, axes, bins=256, cmap=plt.cm.gray):
    """Plot an image along with its histogram and cumulative histogram.
    
    This is taken directly from the scikit image examples page.
        http://scikit-image.org/docs/dev/auto_examples/plot_equalize.html

    """
    img = img_as_float(img)
    ax_img, ax_hist = axes
    ax_cdf = ax_hist.twinx()

    # Display image
    ax_img.imshow(img, cmap)
    ax_img.set_axis_off()

    # Display histogram
    ax_hist.hist(img.ravel(), bins=bins, histtype='step', color='black')
    ax_hist.ticklabel_format(axis='y', style='scientific', scilimits=(0, 0))
    ax_hist.set_xlabel('Pixel intensity')
    ax_hist.set_xlim(0, 1)
    ax_hist.set_yticks([])

    # Display cumulative distribution
    img_cdf, bins = exposure.cumulative_distribution(img, bins)
    ax_cdf.plot(bins, img_cdf, 'r')
    ax_cdf.set_yticks([])

    return ax_img, ax_hist, ax_cdf


# Courtesy of Guilaume Gay via Scikit Image mailing list
def preprocess_highpass(image, filter_width=100):
    """ Emulates a highpass filter by subtracted a smoothed version 
    of the image from the image.

    Parameters:
    ----------------
    image: a ndarray
    filter_width: an int, should be much bigger than the relevant features in the image, 
        and about the scale of the background variations

    Returns:
    -----------
    f_image: ndarray with the same shape as the input image, with float dtype, the filtered image,
        with minimum at 0.
    """

    image = img_as_float(image)
    lowpass = ndimage.gaussian_filter(image, filter_width)
    f_image = image - lowpass
    f_image -= f_image.min()
    return f_image


def _get_xyshape(image):
    """Returns first two dimensions of an image, whether it is 2d or 3d, 
       as is the case of colored images.

    Parameters
    ----------
    image: a ndarray
    
    Returns:
    -----------
    img_xf, img_yf: shape of first and second dimension of array
    
    Raises
    ------
    UtilsError
        If image shape is not 2 or 3.
    
    """

    ndim = len(image.shape)

    if ndim == 3:
        img_xf, img_yf, z = image.shape

    elif ndim == 2:
	img_xf, img_yf = image.shape

    else:
	raise UtilsError('Image must have dimensions 2 or 3 (received %s)' % ndim)

    return img_xf, img_yf


def crop(image, coords):
    """Crops a rectangle (xi, yi, xf, yf) from an image.  If image
       is 3-dimenionsal (eg color image), slices on first two dimensions.

    Parameters
    ----------
    image: a ndarray
    coords : (xi, yi, xf, yf)
        lenngth-4 iterable with coordiantes corresponding to rectangle corners
	in order (xi, yi, xf, yf)

    Notes
    -----
    Allows for xf/yf > xi/yi for more flexible rectangle drawing.
    Please refer to the numpy indexing API for de-facto slicing. 

    Raises
    ------
    UtilsError
    	If more or less than 4 coordinates are passed.
        If x or y rectangle coordinates exceed the range of image (image.shape)


    Examples
    --------
    >>> from skimage import data
    >>> lena = img_as_float(data.lena())
    >>> crop(lena, (0,0,400,300))	
	
    """

    img_xf, img_yf = _get_xyshape(image)
    
    try:
        xi, yi, xf, yf = coords
    except Exception:
	raise UtilsError("Coordinates must be lenth four iterable of form"
	    "(xi, yi, xf, yf).  Instead, received %s" % coords)


    # Make sure crop limits are in range of image
    for x in (xi, xf):
        if x < 0 or x > img_xf:
	    raise UtilsError('Cropping bounds (%s, %s) exceed'
                ' image horizontal range (%s, %s)' % (xi, xf, 0, img_xf))

    for y in (yi, yf):
        if y < 0 or y > img_yf:
    	    raise UtilsError('Cropping bounds (%s, %s) exceed'
                ' image vertical range (%s, %s)' % (yi, yf, 0, img_yf))

    # Reverse bounds if final exceeds initial
    if yf < yi:
	yi, yf = yf, yi

    if xf < xi:
	xi, xf = xf, xi

    ndim = len(image.shape)
    if ndim == 3:
        image = image[yi:yf, xi:xf, :]
    else:
	image = image[yi:yf, xi:xf]   

    return image


### CUSTOM PLOTS ###

def scaleshow(image, *imshowargs, **imshowkwds):
    
    converter = imshowkwds.pop('converter', None)
    if converter:

        # Modify the extent
        extent = imshowkwds.pop('extent', None)
	if not extent:
	    xmax, ymax = _get_xyshape(image)
	    extent = (0,ymax, xmax, 0)
	#Convert 
	imshowkwds['extent'] = converter.convert(extent)
	
    axesimage = imshow(image, *imshowargs, **imshowkwds)
    if converter:
        axesimage.axes.set_xlabel(converter.baseunit)
        axesimage.axes.set_ylabel(converter.baseunit)
    return axesimage
    

def zoom(image, coords, *imshowargs, **imshowkwds):
    """
    Plot zoomed-in region of rectangularly cropped image'
   
    Parameters
    ----------
    image: a ndarray
    coords : (xi, yi, xf, yf)
        lenngth-4 iterable with coordiantes corresponding to rectangle corners
	in order (xi, yi, xf, yf)
    *imshowargs, **imshowkwds : plotting *args, **kwargs
        Passed directly to matplotlib imshow()

    Returns
    -------
    Matplotlib Axes
        This is the output of imshow(image, *imshowargs, **imshowkwds)

    Notes
    -----
    Simple wrapper that calls crop, then imshow() on the cropped image.

    Examples
    --------
    >>> from skimage import data
    >>> lena = img_as_float(data.lena())
    >>> zoom(lena, (0,0,400,300), plt.cm.gray);

    """    

    cropped_image = crop(image, coords)
    return scaleshow(cropped_image, *imshowargs, **imshowkwds)    


def zoomshow(image, coords, *imshowargs, **imshowkwds):
    """
    Plot full and cropped image side-by-side. 
    Draws a rectangle on full image to show zooming coordinate.
             
    Parameters
    ----------
    image: a ndarray
    coords : (xi, yi, xf, yf)
        lenngth-4 iterable with coordiantes corresponding to rectangle corners
	in order (xi, yi, xf, y
      
    *imshowargs, **imshowkwds : plotting *args, **kwargs
         Passed directly to matplotlib imshow() after removing special keywords
	 (SEE NOTES)
	  
     Returns
     -------
     cropped_image, (plots) : tuple
	   image, (ax_full, ax_zoomed) 
 
     Notes
     -----
     Returns both the cropped image and the plots for flexibility.  Plots 
     are returned in this manner to allow user to further draw on them before
     calling show().
     
     Rectangle has special plotting keywords- "lw", "ls", "color", "orient"
     
     Examples
     --------
     >>> from skimage import data
     >>> lena = img_as_float(data.lena())
     >>> zoomshow(lena, (0,0,400,300), plt.cm.gray, orient='v', color='r');

    """
    
    # Pop keywords for rectangle
    lw = imshowkwds.pop('lw', '2')
    ls = imshowkwds.pop('ls', '-')
    color = imshowkwds.pop('color', 'y')
    orient = imshowkwds.pop('orient', 'h')
    
    if orient in ['h', 'horizontal']:
        subshape = {'nrows':1, 'ncols':2}
    elif orient in ['v', 'vertical']:
        subshape = {'nrows':2, 'ncols':1}
    else:
        raise UtilsError('Plot orientation "%s" not understood' % orient)
    
    # Normalize coordinates for axhline/axvline
    img_ymax, img_xmax = _get_xyshape(image)

    if len(coords) != 4:
	raise UtilsError("Coordinates must be lenth four iterable of form"
	    "(xi, yi, xf, yf).  Instead, received %s" % coords)

    xi, yi, xf, yf = coords

    xi_norm, xf_norm = xi / img_xmax, xf / img_xmax
    yi_norm, yf_norm = (img_ymax - yi) / img_ymax, \
        (img_ymax - yf) / img_ymax
    
    f, (ax_full, ax_zoomed) = plt.subplots(**subshape)
               
    ax_full.imshow(image, *imshowargs, **imshowkwds)      
    cropped_image = crop(image, coords) 
    ax_zoomed.imshow(cropped_image, *imshowargs, **imshowkwds)

    # Add rectangle
    ax_full.axhline(y=yi, xmin=xi_norm, xmax=xf_norm, 
        linewidth=lw, color=color, ls=ls)
    ax_full.axhline(y=yf, xmin=xi_norm, xmax=xf_norm, 
        linewidth=lw, color=color, ls=ls)
    ax_full.axvline(x=xi, ymax=yi_norm, ymin=yf_norm, 
        linewidth=lw, color=color, ls=ls)
    ax_full.axvline(x=xf, ymax=yi_norm, ymin=yf_norm, 
        linewidth=lw, color=color, ls=ls)
    
    return cropped_image, (ax_full, ax_zoomed)


### COLOR RELATED UTILITIES ###
def _RGBcolorize(image):
    if len(image.shape) == 2:
	if image.dtype == bool:
	    return label2rgb(image)
	else:
	    return dstack((image, image, image))
    return image


def color_overlay(img_under, img_over, hue = 0.4, sat = 1.0):
    """
    blah blah blah

    Parameters
    ----------
    img_under : ndarray
        "Bottom" image

    img_over : ndarray
        "Top" image	
	
    Returns
    -------
    bar : float
        blah blah ...
        blah blah ...

    Raises
    ------
    MyException
       If condition foo is met or not met...
       blah blah ...

    Notes
    -----
    blah blah blah
    blah blah blah

    See Also
    --------
    baz : description of baz
    
    Examples
    --------
    >>> np.linspace(2.0, 3.0, num=5)
        array([ 2.  ,  2.25,  2.5 ,  2.75,  3.  ])
    >>> np.linspace(...)
        ...

    Graphical illustration:

    >>> import matplotlib.pyplot as plt
    >>> N = 8
    ...
    >>> plt.show()

    """
    
    # Turn images to RGB
    img_under, img_over = _RGBcolorize(img_under), _RGBcolorize(img_over)
    
    # From RGB, convert to HSV
    under_hsv = rgb2hsv(img_under)
    over_hsv = rgb2hsv(img_over)
    
    # Modify the under image hsv by the overlay's hsv
#    under_hue, over_hue = under_hsv[..., 0], overhsv[..., 0]
#    under_sat, over_sat = under_hsv[..., 1], overhsv[..., 1]
#    under_val, over_val = under_hsv[..., 2], overhsv[..., 2]


    under_hsv[..., 0] = over_hsv[..., 0] * hue
    under_hsv[..., 1] = over_hsv[..., 1] * sat
    
    # Revert to RGB and return overlaid image
    return hsv2rgb(under_hsv)


    