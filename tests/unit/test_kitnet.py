"""Plan de Pruebas Unitarias PU-04: Modulo KitNET/KitNET.py.

Evalua inicializacion con valores por defecto, proteccion RuntimeError, mapeo
predefinido y ciclo completo FM train -> AD train -> AD execute mediante process(x).
"""

from __future__ import annotations

import numpy as np
import pytest

from KitNET.KitNET import KitNET


@pytest.mark.unit
class TestKitNET:
    """Suite consolidada de pruebas unitarias para la clase orquestadora KitNET (2 casos)."""

    def test_ut_kn_001_init_runtime_guard_and_predefined_map(self, rng: np.random.Generator) -> None:
        """UT-KN-001: Verifica defaults/clamping, RuntimeError sin mapeo y ejecucion con feature_map predefinido."""
        # 1. Defaults y herencia de FM_grace_period
        kn_def = KitNET(n=10, max_autoencoder_size=0, FM_grace_period=None, AD_grace_period=500)
        assert kn_def.FM_grace_period == 500 and kn_def.AD_grace_period == 500
        assert kn_def.m == 1 and kn_def.v is None and kn_def.outputLayer is None and kn_def.ensembleLayer == []

        # 2. Guarda RuntimeError antes de aprender mapeo
        kn_guard = KitNET(n=6, max_autoencoder_size=3, FM_grace_period=10, AD_grace_period=20)
        with pytest.raises(RuntimeError, match="feature mapping has not yet been learned"):
            kn_guard.execute(np.ones(6, dtype=np.float64))

        # 3. Mapeo predefinido salta fase FM
        custom_map = [[0, 1, 2], [3, 4], [5]]
        kn_map = KitNET(n=6, max_autoencoder_size=3, FM_grace_period=0, AD_grace_period=5, feature_map=custom_map)
        assert kn_map.v == custom_map and len(kn_map.ensembleLayer) == 3
        assert kn_map.outputLayer is not None and kn_map.outputLayer.params.n_visible == 3

        for _ in range(6):
            assert kn_map.process(rng.normal(0.0, 1.0, size=6)) == 0.0
        assert float(kn_map.process(rng.normal(0.0, 1.0, size=6))) > 0.0
        assert kn_map.n_executed == 1

    def test_ut_kn_002_full_lifecycle_fm_to_ad_to_execute(self, rng: np.random.Generator) -> None:
        """UT-KN-002: Verifica transicion completa FM train -> AD train -> AD execute mediante process(x)."""
        n_features, fm_grace, ad_grace = 12, 10, 15
        kn = KitNET(
            n=n_features,
            max_autoencoder_size=4,
            FM_grace_period=fm_grace,
            AD_grace_period=ad_grace,
            learning_rate=0.1,
            hidden_ratio=0.75,
        )

        # Fase 1: FM learning (fm_grace + 1 paquetes)
        for _ in range(fm_grace):
            assert kn.process(rng.uniform(1.0, 10.0, size=n_features)) == 0.0
            assert kn.v is None

        assert kn.process(rng.uniform(1.0, 10.0, size=n_features)) == 0.0
        assert kn.v is not None and all(len(c) <= 4 for c in kn.v)
        assert len(kn.ensembleLayer) == len(kn.v) and kn.outputLayer is not None

        # Fase 2: AD training
        for _ in range(ad_grace):
            assert kn.process(rng.uniform(1.0, 10.0, size=n_features)) == 0.0
        assert kn.n_trained == fm_grace + ad_grace + 1 and kn.n_executed == 0

        # Fase 3: AD execution
        rmse_score = float(kn.process(rng.uniform(1.0, 10.0, size=n_features)))
        assert rmse_score > 0.0 and not np.isnan(rmse_score) and kn.n_executed == 1
