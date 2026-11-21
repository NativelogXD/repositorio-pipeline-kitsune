"""Plan de Pruebas Unitarias PU-02: Modulo KitNET/dA.py (Denoising Autoencoder).

Evalua inicializacion por hiddenRatio, reproducibilidad determinista, corrupcion binomial,
normalizacion min-max online, compuerta de periodo de gracia y convergencia SGD.
"""

from __future__ import annotations

import numpy as np
import pytest

from KitNET.dA import dA, dA_params


@pytest.mark.unit
class TestDenoisingAutoencoder:
    """Suite consolidada de pruebas unitarias para dA_params y dA (2 casos)."""

    def test_ut_da_001_init_reproducibility_and_corruption(self) -> None:
        """UT-DA-001: Verifica n_hidden=ceil(n_visible*hiddenRatio), semilla fija 1234 y corrupcion binomial."""
        params = dA_params(n_visible=10, n_hidden=0, lr=0.1, corruption_level=0.0, gracePeriod=100, hiddenRatio=0.75)
        ae = dA(params)
        assert ae.params.n_hidden == 8
        assert ae.W.shape == (10, 8)
        assert ae.W_prime.shape == (8, 10)
        assert ae.hbias.shape == (8,)
        assert ae.vbias.shape == (10,)
        np.testing.assert_allclose(ae.W_prime, ae.W.T)
        bound = 1.0 / 10.0
        assert np.all((ae.W >= -bound) & (ae.W <= bound))

        # Reproducibilidad determinista con semilla interna 1234
        ae1 = dA(dA_params(n_visible=6, hiddenRatio=0.5))
        ae2 = dA(dA_params(n_visible=6, hiddenRatio=0.5))
        np.testing.assert_array_equal(ae1.W, ae2.W)

        # Corrupcion binomial valida e invalida
        ae_corr = dA(dA_params(n_visible=20, corruption_level=0.3))
        x = np.ones(20, dtype=np.float64) * 5.0
        corrupted = ae_corr.get_corrupted_input(x, 0.3)
        assert corrupted.shape == x.shape
        assert np.all(np.isin(corrupted, [0.0, 5.0]))
        assert ae_corr.train(x) >= 0.0

        with pytest.raises(AssertionError):
            ae_corr.get_corrupted_input(x, 1.0)

    def test_ut_da_002_minmax_grace_gating_and_sgd_convergence(self, rng: np.random.Generator) -> None:
        """UT-DA-002: Verifica normalizacion min-max online, inGrace/execute y convergencia SGD."""
        # 1. Seguimiento de extremos min-max
        ae_norm = dA(dA_params(n_visible=3, hiddenRatio=0.75, gracePeriod=0))
        x1 = np.array([10.0, -5.0, 0.0], dtype=np.float64)
        x2 = np.array([2.0, 8.0, -3.0], dtype=np.float64)
        assert ae_norm.train(x1) >= 0.0
        np.testing.assert_array_equal(ae_norm.norm_min, x1)
        np.testing.assert_array_equal(ae_norm.norm_max, x1)
        assert ae_norm.train(x2) >= 0.0
        np.testing.assert_array_equal(ae_norm.norm_min, np.array([2.0, -5.0, -3.0]))
        np.testing.assert_array_equal(ae_norm.norm_max, np.array([10.0, 8.0, 0.0]))
        assert ae_norm.n == 2

        # 2. Compuerta de periodo de gracia
        ae_grace = dA(dA_params(n_visible=4, lr=0.1, gracePeriod=3, hiddenRatio=0.75))
        sample = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float64)
        assert ae_grace.inGrace() is True
        assert ae_grace.execute(sample) == 0.0
        for idx in range(3):
            ae_grace.train(sample + float(idx))
        assert ae_grace.inGrace() is False
        assert float(ae_grace.execute(sample)) > 0.0

        # 3. Convergencia SGD y discriminacion de anomalias
        ae_conv = dA(dA_params(n_visible=5, lr=0.15, corruption_level=0.0, gracePeriod=10, hiddenRatio=0.8))
        base_pattern = np.array([0.2, 0.8, 0.4, 0.6, 0.5], dtype=np.float64)
        ae_conv.train(np.zeros(5, dtype=np.float64))
        ae_conv.train(np.ones(5, dtype=np.float64))

        initial_rmse = float(ae_conv.train(base_pattern))
        final_rmse = initial_rmse
        for _ in range(150):
            noisy = np.clip(base_pattern + rng.normal(0.0, 0.005, size=5), 0.0, 1.0)
            final_rmse = float(ae_conv.train(noisy))
        assert final_rmse < initial_rmse

        normal_rmse = float(ae_conv.execute(base_pattern))
        anomaly_rmse = float(ae_conv.execute(np.array([5.0, -4.0, 6.0, -3.0, 4.5], dtype=np.float64)))
        assert anomaly_rmse > normal_rmse
