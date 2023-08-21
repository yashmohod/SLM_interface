import SLM_interface.pyhot as pyhot
import numpy as np
import pytest

# Currently, just test that the interface runs, not for physical correctness


class TestClass:
    def setup_method(self):
        self.mySLM = pyhot.SLM(512, 512, 8., 1.064, 3333.33, random_seed = 1234)
        self.points = np.array([[3., 5., 0],
                                [-7., -4, 2.]])
        self.one_point = np.array([[-5., 1., -4.]])

    def test_spl(self):
        self.mySLM.calc_holo(self.points, method = 'spl')

    def test_rs(self):
        self.mySLM.calc_holo(self.points, method = 'rs')

    def test_rm(self):
        self.mySLM.calc_holo(self.points, method = 'rm')

    def test_wgs(self):
        self.mySLM.calc_holo(self.points, method = 'wgs')

    def one_point_equality(self):
        # Algorithms should agree for a single point hologram
        spl = self.mySLM.calc_holo(self.one_point, method = 'spl')
        rm = self.mySLM.calc_holo(self.one_point, method = 'rm')
        assert np.array_equal(rm, spl)

    def test_ft_intensity(self):
        holo = self.mySLM.calc_holo(self.one_point, method = 'spl')
        intensity = pyhot.calc_fourier_amplitude(holo)

    def test_trap_field(self):
        phase = self.mySLM._calc_single_pt_phase(self.one_point[0])
        Vm = self.mySLM.trap_field(self.one_point[0], phase)
        np.abs(Vm) == pytest.approx(1)

        phase2 = self.mySLM._calc_phase_wgs(self.points)
        V0 = self.mySLM.trap_field(self.points[0], phase2)
        V1 = self.mySLM.trap_field(self.points[1], phase2)
        print(np.abs(V0)**2)
        print(np.abs(V1)**2)
