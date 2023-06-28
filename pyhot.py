'''
pyhot.py

Calculation of holograms to be displayed on a spatial light modulator
to create optical traps in holographic optical tweezers.

Author: Jerome Fung (jfung@ithaca.edu)
'''

import numpy as np
# import numba

class SLM(object):

    def __init__(self, nx, ny, px, wavelen, f):
        '''
        '''
        self.nx = nx
        self.ny = ny
        self.px = px
        self.wavelen = wavelen
        self.f = f

        # TODO: calculate pixel coordinates once and for all
        # I think we need to center the image
        self.xs, self.ys = np.mgrid[0:nx, 0:ny]
        self.xs = (self.xs - self.nx/2) * self.px # dimensional
        self.ys = (self.ys - self.ny/2) * self.px
        
    def calc_holo(self, pts, method = 'spl'):
        if method == 'spl':
            return self._calc_holo_spl(pts)
        else:
            raise NotImplementedError

    def _calc_holo_spl(self, pts):
        '''
        Calculate hologram using superposition of prisms and lenses.
        '''

        holo_sum = np.zeros((self.nx, self.ny), dtype = np.complex128)
        
        for pt in pts:
            Delta_m_lens = np.pi * pt[2] / (self.wavelen * self.f**2) * \
                (self.xs**2 + self.ys**2)
            Delta_m_grating = 2 * np.pi / (self.wavelen * self.f) * (
                self.xs * pt[0] + self.ys * pt[1])
            Delta_m = Delta_m_lens + Delta_m_grating
            holo_sum += np.exp(1j * Delta_m)

        # np.angle between -pi and pi, shift to 0 to 2 pi 
        holo = np.angle(holo_sum) + np.pi

        # scale to 8 bit
        holo = holo * 255 / (2 * np.pi)

        # round
        return np.ushort(np.around(holo))