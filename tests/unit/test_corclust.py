"""Plan de Pruebas Unitarias PU-03: Modulo KitNET/corClust.py.

Evalua la inicializacion de estructuras, actualizacion incremental de residuos,
matriz de distancias de correlacion sin NaN y particion jerarquica del dendrograma.
"""

from __future__ import annotations

import numpy as np
import pytest

from KitNET.corClust import corClust


@pytest.mark.unit
class TestCorClust:
    """Suite consolidada de pruebas unitarias para corClust (2 casos)."""

    def test_ut_cc_001_init_incremental_update_and_corr_dist_guard(self) -> None:
        """UT-CC-001: Verifica estado inicial, update incremental y guarda contra varianza cero en corrDist()."""
        cc_init = corClust(n=8)
        assert cc_init.n == 8 and cc_init.N == 0
        assert cc_init.c.shape == (8,) and cc_init.c_r.shape == (8,) and cc_init.c_rs.shape == (8,)
        assert cc_init.C.shape == (8, 8) and np.all(cc_init.C == 0.0)

        # Actualizacion incremental de estadisticos
        cc_upd = corClust(n=3)
        cc_upd.update(np.array([1.0, 2.0, 3.0], dtype=np.float64))
        assert cc_upd.N == 1
        np.testing.assert_allclose(cc_upd.c, np.array([1.0, 2.0, 3.0]))
        np.testing.assert_allclose(cc_upd.c_r, np.zeros(3))

        cc_upd.update(np.array([2.0, 4.0, 6.0], dtype=np.float64))
        assert cc_upd.N == 2
        np.testing.assert_allclose(cc_upd.c, np.array([3.0, 6.0, 9.0]))
        assert np.all(np.diag(cc_upd.C) > 0.0)
        np.testing.assert_allclose(cc_upd.C, cc_upd.C.T, rtol=1e-12)

        # Matriz de distancia con caracteristicas constantes (guarda contra 0/0)
        cc_const = corClust(n=4)
        for i in range(10):
            cc_const.update(np.array([float(i), float(2 * i), 0.0, 5.0], dtype=np.float64))
        dist_matrix = cc_const.corrDist()
        assert dist_matrix.shape == (4, 4)
        assert not np.any(np.isnan(dist_matrix)) and not np.any(np.isinf(dist_matrix))
        assert np.all(dist_matrix >= 0.0)

    def test_ut_cc_002_clustering_partition_and_boundary_clamping(self, rng: np.random.Generator) -> None:
        """UT-CC-002: Verifica particion completa <= maxClust y clamping en limites extremos (<1 y >n)."""
        n_features, max_clust = 15, 4
        cc = corClust(n=n_features)
        for _ in range(40):
            cc.update(rng.normal(0.0, 1.0, size=n_features))

        feature_map = cc.cluster(maxClust=max_clust)
        assert isinstance(feature_map, list)
        assert all(1 <= len(group) <= max_clust for group in feature_map)
        flattened = [idx for group in feature_map for idx in group]
        assert sorted(flattened) == list(range(n_features))

        # Clamping en extremos
        cc_clamp = corClust(n=6)
        for _ in range(15):
            cc_clamp.update(rng.uniform(0.0, 10.0, size=6))
        map_singletons = cc_clamp.cluster(maxClust=0)
        assert len(map_singletons) == 6 and all(len(g) == 1 for g in map_singletons)
        map_single_group = cc_clamp.cluster(maxClust=100)
        assert len(map_single_group) == 1 and sorted(map_single_group[0]) == list(range(6))
