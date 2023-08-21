'''
pyhot.py

Calculation of holograms to be displayed on a spatial light modulator
to create optical traps in holographic optical tweezers.

Author: Jerome Fung (jfung@ithaca.edu)
'''

import numpy as np
import numpy.fft as fft
# import numba

class SLM(object):

    def __init__(self, nx, ny, px, wavelen, f, random_seed = None):
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

        # 1D array of locations
        self.xs_r = self.xs.ravel()
        self.ys_r = self.ys.ravel()
        self.npix = len(self.xs_r)
        self.holo_indices = np.arange(len(self.xs_r))

        if random_seed is None:
            self.rng = np.random.default_rng()
        else:
            self.rng = np.random.default_rng(seed = random_seed)

    def calc_holo(self, pts, method = 'spl'):
        if method == 'spl':
            return convert_and_scale(self._calc_phase_spl(pts))
        elif method == 'rs':
            return convert_and_scale(self._calc_phase_rs(pts))
        elif method == 'rm':
            return convert_and_scale(self._calc_phase_rm(pts))
        elif method == 'wgs':
            return convert_and_scale(self._calc_phase_wgs(pts))
        else:
            raise NotImplementedError

    def _calc_phase_spl(self, pts):
        '''
        Calculate hologram using superposition of prisms and lenses.

        '''

        holo_sum = np.zeros((self.nx, self.ny), dtype = np.complex128)

        for pt in pts:
            holo_sum += np.exp(1j*self._calc_single_pt_phase(pt))

        return np.angle(holo_sum) + np.pi

    def _calc_phase_rs(self, pts):
        '''
        Calculate hologram using random superposition, adding a randomly-chosen
        phase factor to the hologram associated with each point trap.
        '''
        holo_sum = np.zeros((self.nx, self.ny), dtype = np.complex128)

        random_phases = self.rng.random(len(pts)) * 2 * np.pi

        for pt, phase in zip(pts, random_phases):
            holo_sum += np.exp(1j*(self._calc_single_pt_phase(pt) + phase))

        return np.angle(holo_sum) + np.pi

    def _calc_phase_rm(self, pts):
        '''
        Calculate holograms using random mask encoding. For N trap points,
        a randomly-chosen subset of 1/N of the hologram points display
        the hologram associated with any given trap.
        '''
        holo = np.zeros(self.npix)
        shuffled_indices = self.rng.permuted(self.holo_indices)
        npix_over_M = np.floor(self.npix/len(pts)).astype('int')

        for pt_index, point in zip(np.arange(len(pts)), pts):
            lower_ind = pt_index * npix_over_M
            upper_ind = (pt_index + 1) * npix_over_M
            holo[shuffled_indices[lower_ind:upper_ind]] = \
                self._calc_single_pt_phase(point,
                                           self.xs_r[shuffled_indices[lower_ind:upper_ind]],
                                           self.ys_r[shuffled_indices[lower_ind:upper_ind]])

        return holo.reshape((self.nx, self.ny)) % (2 * np.pi)


    def _calc_single_pt_phase(self, pt, xs = None, ys = None):
        '''
        Grating-and-lens phase for hologram to produce a single point trap.
        See di Leonardo, Ianni, Ruocco eqn (2).
        '''
        if xs is None:
            xs = self.xs
        if ys is None:
            ys = self.ys

        Delta_m_lens = np.pi * pt[2] / (self.wavelen * self.f**2) * \
            (xs**2 + ys**2)
        Delta_m_grating = 2 * np.pi / (self.wavelen * self.f) * (
            xs * pt[0] + ys * pt[1])
        return Delta_m_lens + Delta_m_grating


    def _calc_phase_wgs(self, pts, max_eps = 1e-3, max_iter = 30):
        '''Calculate hologram using weighted Gerchberg-Saxton algorithm,
        as in di Leonardo et al.
        '''
        n_traps = len(pts)

        # initialize
        weights = np.ones(n_traps)
        phase = self._calc_phase_rs(pts)
        prev_phase = np.ones((self.nx, self.ny))

        iter_cnt = 0
        for n_iter in np.arange(max_iter):
            # calculate trap fields
            fields = np.array([self.trap_field(pt, phase) for pt in pts])
            av_field = np.average(np.abs(fields))
            # update weights
            weights = weights * av_field / np.abs(fields)

            # update phase
            phase_sum = np.zeros((self.nx, self.ny), dtype = np.complex128)

            for pt, ctr in zip(pts, np.arange(n_traps)):
                phase_sum += np.exp(1j*self._calc_single_pt_phase(pt)) * \
                    weights[ctr] * fields[ctr] / np.abs(fields[ctr])

            # test for convergence
            new_phase = np.angle(phase_sum) + np.pi
            eps = np.abs((new_phase - phase)/phase)
            prev_eps = np.abs((new_phase - prev_phase)/prev_phase)
            if (eps < max_eps).all() or (prev_eps < max_eps).all(): # converged
                phase = new_phase
                break
            else:
                prev_phase = phase
                phase = new_phase
                iter_cnt += 1

        print(iter_cnt)
        return phase


    def trap_field(self, point, phase_pattern):
        '''Calculate nondimensional trap field V_m for a trap located
           at point given hologram phase_pattern.
           See Eq. (3) of di Leonardo, Ianni, and Ruocco (2007)
        '''
        pt_phase = self._calc_single_pt_phase(point)
        return np.exp(1j*(phase_pattern - pt_phase)).sum() / self.npix


def convert_and_scale(raw_holo):
    # np.angle between -pi and pi, shift to 0 to 2 pi
    holo = raw_holo
    # scale to 8 bit
    holo = holo * 255 / (2 * np.pi)
    # round
    return np.ushort(np.around(holo))


def calc_fourier_amplitude(holo):
    '''
    Utility function to calculate the field in the trapping plane
    that would be produced by a given hologram.
    '''
    phase = holo * (2 * np.pi) / 255
    field = np.exp(1j*phase)
    return np.abs(fft.fftshift(fft.fft2(field)))**2
