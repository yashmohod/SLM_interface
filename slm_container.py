'''
slm_container.py 
'''

import os
import numpy as np
import yaml
import pyhot


class SLMContainer(object):
    def __init__(self):
        gui_dir_abs_path = os.path.dirname(os.path.abspath(__file__))
        config_fname = os.path.abspath(gui_dir_abs_path) + os.sep + 'optical_train_config.yaml'
        with open(config_fname, mode = 'r') as file:
            config = yaml.safe_load(file)
        
        self.wavelength = config['wavelength']
        self.slm_pixel_size = config['slm_pixel_size']
        self.slm_display_shape = tuple(config['slm_display_shape'])
        
