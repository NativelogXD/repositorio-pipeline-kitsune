"""Plan de Pruebas Unitarias PU-05: Modulo AfterImage.py.

Evalua estadisticas incrementales amortiguadas 1D (incStat), covarianza 2D (incStat_cov)
y la base de datos hash en memoria de flujos (incStatDB) con poda de registros.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from AfterImage import incStat, incStat_cov, incStatDB


@pytest.mark.unit
class TestAfterImage:
    """Suite consolidada de pruebas unitarias para AfterImage.py (2 casos)."""

    def test_ut_ai_001_1d_decay_jitter_headers_and_cov2d(self) -> None:
        """UT-AI-001: Verifica decaimiento 1D, modo jitter, radio/magnitud, headers y covarianza 2D."""
        # 1. Decaimiento exponencial 1D y momentos
        stat = incStat(Lambda=1.0, ID="flow_A", init_time=0.0, isTypeDiff=False)
        stat.insert(v=10.0, t=0.0)
        assert np.isclose(stat.weight(), 1.0) and np.isclose(stat.mean(), 10.0)
        assert np.isclose(stat.var(), 0.0) and np.isclose(stat.std(), 0.0)

        stat.insert(v=20.0, t=1.0)
        assert np.isclose(stat.weight(), 1.5, atol=1e-12)
        assert np.isclose(stat.mean(), 25.0 / 1.5, atol=1e-12)
        assert stat.var() > 0.0 and np.isclose(stat.std(), math.sqrt(stat.var()), atol=1e-12)

        # 2. Modo jitter (isTypeDiff=True)
        jit = incStat(Lambda=0.5, ID="jitter_AB", init_time=10.0, isTypeDiff=True)
        jit.insert(v=999.0, t=10.0)
        assert np.isclose(jit.mean(), 0.0, atol=1e-12)
        jit.insert(v=999.0, t=12.0)
        assert jit.mean() > 0.0 and jit.lastTimestamp == 12.0

        # 3. Magnitud, radio y headers 1D/2D
        s1 = incStat(Lambda=1.0, ID="host1", init_time=0.0)
        s2 = incStat(Lambda=1.0, ID="host2", init_time=0.0)
        s1.insert(v=3.0, t=0.0)
        s2.insert(v=4.0, t=0.0)
        assert np.isclose(s1.magnitude([s2]), 5.0, atol=1e-9)
        assert np.isclose(s1.radius([s2]), 0.0, atol=1e-9)
        assert s1.getHeaders_1D(suffix=True) == ["weight_host1", "mean_host1", "std_host1"]
        assert s1.getHeaders_1D(suffix=False) == ["weight_0", "mean_0", "std_0"]
        hdrs_2d = s1.getHeaders_2D(ID2="host2", suffix=True)
        assert len(hdrs_2d) == 7 and "covariance__host1__host2" in hdrs_2d and "pcc__host1__host2" in hdrs_2d

        # 4. Covarianza y PCC 2D (incStat_cov)
        a = incStat(Lambda=0.1, ID="A", init_time=0.0)
        b = incStat(Lambda=0.1, ID="B", init_time=0.0)
        cov_tracker = incStat_cov(a, b, init_time=0.0)
        a.covs.append(cov_tracker)
        b.covs.append(cov_tracker)
        for step in range(1, 8):
            a.insert(v=float(step * 10), t=float(step))
            b.insert(v=float(step * 20), t=float(step) + 0.1)

        assert len(cov_tracker.get_stats1()) == 2 and len(cov_tracker.get_stats2()) == 4
        assert len(cov_tracker.get_stats3()) == 8 and len(cov_tracker.get_stats4()) == 10
        assert not np.any(np.isnan(cov_tracker.get_stats4()))
        assert np.isclose(a.cov("B"), cov_tracker.cov(), rtol=1e-12)
        assert np.isclose(a.pcc("B"), cov_tracker.pcc(), rtol=1e-12)
        assert a.cov_pcc("B") == cov_tracker.get_stats1()
        assert len(a.allstats_2D("B")) == 7
        assert np.isnan(a.cov("UNKNOWN")[0]) and np.isnan(a.pcc("UNKNOWN")[0])
        assert all(np.isnan(val) for val in a.cov_pcc("UNKNOWN"))
        for ver, expected_len in [(1, 2), (2, 4), (3, 8), (4, 5), (5, 10)]:
            assert len(cov_tracker.getHeaders(ver=ver, suffix=True)) == expected_len

    def test_ut_ai_002_incstatdb_limits_queries_and_cleanup(self) -> None:
        """UT-AI-002: Verifica LookupError por limite, NaN en flujos ausentes, 1D/2D/nD y poda cleanOutOldRecords."""
        # 1. Limite de capacidad
        db_lim = incStatDB(limit=2)
        db_lim.register("host_1", Lambda=1.0)
        db_lim.register("host_2", Lambda=1.0)
        db_lim.register("host_1", Lambda=1.0)
        with pytest.raises(LookupError, match="would exceed incStatHT 1D limit"):
            db_lim.register("host_3", Lambda=1.0)

        # 2. Consultas sobre claves inexistentes
        db = incStatDB(limit=100, default_lambda=1.0)
        res_1d = db.get_1D_Stats("non_existent", Lambda=1.0)
        res_2d = db.get_2D_Stats("non_existent_1", "non_existent_2", Lambda=1.0)
        stats_all, ids_all = db.get_all_2D_Stats("non_existent", Lambda=1.0)
        assert len(res_1d) == 3 and np.all(np.isnan(res_1d))
        assert len(res_2d) == 2 and np.all(np.isnan(res_2d))
        assert stats_all == [] and ids_all == []

        # 3. Actualizaciones, consultas directas y poda
        vec_7d = db.update_get_1D2D_Stats("10.0.0.1", "10.0.0.2", t1=1.0, v1=64.0, Lambda=1.0)
        assert len(vec_7d) == 7 and not np.any(np.isnan(vec_7d))
        assert len(db.get_nD_Stats(["10.0.0.1", "10.0.0.2"], Lambda=1.0)) == 2
        assert not np.any(np.isnan(db.get_1D_Stats("10.0.0.1", Lambda=1.0)))
        assert not np.any(np.isnan(db.get_2D_Stats("10.0.0.1", "10.0.0.2", Lambda=1.0)))
        all_2d_stats, all_2d_ids = db.get_all_2D_Stats("10.0.0.1", Lambda=1.0)
        assert len(all_2d_stats) == 1 and all_2d_ids == [["10.0.0.1", "10.0.0.2"]]
        assert len(db.update_get_2D_Stats("10.0.0.1", "10.0.0.2", t1=1.5, v1=128.0, Lambda=1.0, level=1)) == 2
        assert len(db.getHeaders_nD(Lambda=1.0, IDs=["10.0.0.1", "10.0.0.2"])) == 2

        removed = db.cleanOutOldRecords(cutoffWeight=0.01, curTime=20.0)
        assert removed == 2 and len(db.HT) == 0
