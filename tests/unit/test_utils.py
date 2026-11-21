"""Plan de Pruebas Unitarias PU-01: Modulo KitNET/utils.py.

Evalua matematicamente las funciones de densidad normal (pdf), CDF logaritmica inversa,
media movil circular (rollmean) y las funciones de activacion neuronal con sus derivadas.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import norm

from KitNET import utils


@pytest.mark.unit
class TestUtils:
    """Suite consolidada de pruebas unitarias para KitNET/utils.py (2 casos)."""

    def test_ut_utils_001_distributions_and_rollmean(self) -> None:
        """UT-UTILS-001: Verifica pdf (puntual y simetria vectorizada), invLogCDF y rollmean circular."""
        # 1. pdf puntual N(0, 1)
        result = float(utils.pdf(0.0, 0.0, 1.0))
        expected = 1.0 / np.sqrt(2.0 * np.pi)
        assert np.isclose(result, expected, rtol=1e-7)

        # 2. pdf simetria vectorizada alrededor de mu
        mu, sigma = 5.0, 2.0
        offsets = np.array([0.5, 1.0, 2.5, 4.0], dtype=np.float64)
        np.testing.assert_allclose(
            utils.pdf(mu - offsets, mu, sigma),
            utils.pdf(mu + offsets, mu, sigma),
            rtol=1e-12,
        )

        # 3. invLogCDF equivalente a norm.logcdf(-z)
        x = np.array([0.0, 1.0, 2.0, 3.0], dtype=np.float64)
        np.testing.assert_allclose(
            utils.invLogCDF(x, 1.0, 0.5),
            norm.logcdf(-(x - 1.0) / 0.5),
            rtol=1e-12,
        )

        # 4. Buffer circular rollmean(k=3)
        rm = utils.rollmean(k=3)
        assert rm.winsize == 3
        assert rm.pointer == 0
        assert np.isclose(rm.apply(3.0), 1.0)
        assert np.isclose(rm.apply(6.0), 3.0)
        assert np.isclose(rm.apply(9.0), 6.0)
        assert rm.pointer == 0
        assert np.isclose(rm.apply(12.0), 9.0)
        assert rm.pointer == 1

    def test_ut_utils_002_neural_activations_and_derivatives(self) -> None:
        """UT-UTILS-002: Verifica sigmoid/dsigmoid, tanh/dtanh, softmax (1D/2D) y ReLU/dReLU."""
        # 1. Sigmoid y dsigmoid
        x_sig = np.array([-10.0, -1.0, 0.0, 1.0, 10.0], dtype=np.float64)
        y_sig = utils.sigmoid(x_sig)
        assert np.isclose(y_sig[2], 0.5, atol=1e-12)
        assert np.all((y_sig > 0.0) & (y_sig < 1.0))
        assert np.all(np.diff(y_sig) > 0.0)

        y_act = np.array([0.1, 0.25, 0.5, 0.75, 0.9], dtype=np.float64)
        np.testing.assert_allclose(utils.dsigmoid(y_act), y_act * (1.0 - y_act), rtol=1e-12)
        assert np.isclose(utils.dsigmoid(0.5), 0.25, atol=1e-12)

        # 2. Tanh y dtanh
        x_tanh = np.array([-2.0, -0.5, 0.0, 0.5, 2.0], dtype=np.float64)
        y_tanh = utils.tanh(x_tanh)
        np.testing.assert_allclose(y_tanh, -utils.tanh(-x_tanh), rtol=1e-12)
        np.testing.assert_allclose(utils.dtanh(y_tanh), 1.0 - y_tanh**2, rtol=1e-12)

        # 3. Softmax 1D (con invarianza al desplazamiento) y 2D
        vec_1d = np.array([1.0, 2.0, 3.0], dtype=np.float64)
        out_1d = utils.softmax(vec_1d)
        assert np.isclose(np.sum(out_1d), 1.0, atol=1e-12)
        np.testing.assert_allclose(out_1d, utils.softmax(vec_1d + 1000.0), rtol=1e-12)

        mat_2d = np.array([[1.0, 2.0, 3.0], [10.0, 20.0, 30.0]], dtype=np.float64)
        out_2d = utils.softmax(mat_2d)
        assert out_2d.shape == (2, 3)
        np.testing.assert_allclose(np.sum(out_2d, axis=1), np.ones(2), atol=1e-12)

        # 4. ReLU y dReLU
        x_relu = np.array([-5.0, -0.01, 0.0, 0.01, 5.0], dtype=np.float64)
        np.testing.assert_allclose(utils.ReLU(x_relu), np.array([0.0, 0.0, 0.0, 0.01, 5.0]))
        np.testing.assert_allclose(utils.dReLU(x_relu), np.array([0.0, 0.0, 0.0, 1.0, 1.0]))
