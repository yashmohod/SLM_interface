'''
thorcam_container.py 

Class for working with Thorlabs USB cameras.
'''

import os
import yaml

from thorlabs_tsi_sdk.tl_camera import TLCameraSDK

class CameraContainer(object):
    def __init__(self):
        gui_dir_abs_path = os.path.dirname(os.path.abspath(__file__))
        config_fname = os.path.abspath(gui_dir_abs_path) + os.sep + 'dll_path_config.yaml'
        with open(config_fname, mode = 'r') as file:
            config = yaml.safe_load(file)
        dll_abs_path = config['dll_absolute_path']
        os.environ['PATH'] = dll_abs_path + os.pathsep + os.environ['PATH']
        os.add_dll_directory(dll_abs_path)
        
        config_fname = os.path.abspath(gui_dir_abs_path) + os.sep + 'camera_config.yaml'
        with open(config_fname, mode = 'r') as file:
            config = yaml.safe_load(file)
            
        self.camera_sensor_shape = config['camera_sensor_shape']
        
        self.sdk = TLCameraSDK()
        
        available_cameras = self.sdk.discover_available_cameras()
        if len(available_cameras) < 1:
            print("no cameras detected")
            self.camera = None
        else:
            self.camera = self.sdk.open_camera(available_cameras[0])
            self.camera.exposure_time_us = 5000 # 5 ms
            self.camera.image_poll_timeout_ms = 1000
            self.camera.frames_per_trigger_zero_for_unlimited = 1
            self.camera.arm(2)
            
    def _cleanup(self):
        if self.camera is not None:
            self.camera.disarm()
            self.camera.dispose()
        self.sdk.dispose()
        print("Camera was closed")
        
