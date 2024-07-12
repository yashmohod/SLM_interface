import numpy as np
import wx

def gray_ndarray_to_wxImage(array, bit_depth = 8):
    '''
    Convert a 2-dimensional grayscale ndarray to a wx.Image.
    Scales array values depending on bit depth.
    
    Note: rows of an ndarray correspond to height and columns to width.
    '''
    h, w = array.shape[:2]
    
    # Normalize image based on bit depth and cast to 8-bit-integer
    # See https://stackoverflow.com/questions/65283588/display-numpy-array-cv2-image-in-wxpython-correctly
    if bit_depth != 8:
        data = array.astype(np.float64) / (2**bit_depth - 1) * 255
        data = data.astype(np.uint8)
    else:
        data = array.astype(np.uint8)

    # Duplicate channels for rgb 
    color_data = np.repeat(data[:, :, np.newaxis], 3, axis = 2)
    
    return wx.ImageFromBuffer(width = w, height = h, dataBuffer = color_data)
    
