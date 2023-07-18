import SLM_interface.pyhot as pyhot
import numpy as np

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

    def test_one_point_equality(self):
        # Algorithms should agree for a single point hologram
        spl = self.mySLM.calc_holo(self.one_point, method = 'spl')
        rm = self.mySLM.calc_holo(self.one_point, method = 'rm')
        rs = self.mySLM.calc_holo(self.one_point, method = 'rs')
        assert np.array_equal(rm, spl)
        assert np.array_equal(rs, spl)
