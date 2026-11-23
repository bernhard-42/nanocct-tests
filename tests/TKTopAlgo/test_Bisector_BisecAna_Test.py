# Translated from OCCT src/ModelingAlgorithms/TKTopAlgo/GTests/Bisector_BisecAna_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.Bisector import Bisector_BisecAna
from nanocct.Geom2d import Geom2d_Ellipse, Geom2d_TrimmedCurve
from nanocct.gp import gp_Ax2d, gp_Dir2d, gp_Pnt2d
from nanocct.Precision import Precision


def test_Bisector_BisecAnaTest_CopyUsesNaturalPeriod():
    ellipse = Geom2d_Ellipse(gp_Ax2d(gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 0.0)), 3.0, 2.0)
    for first in (-1.48, 1.53, -4.75):
        bisector = Bisector_BisecAna()
        bisector.Init(Geom2d_TrimmedCurve(ellipse, first, first + 2.0 * math.pi, True, False))
        copy = bisector.Copy()
        assert isinstance(copy, Bisector_BisecAna), first
        assert 0.0 <= copy.FirstParameter() < 2.0 * math.pi, first
        assert copy.LastParameter() - copy.FirstParameter() == pytest.approx(2.0 * math.pi, abs=Precision.PConfusion_s())
        assert copy.EvalD0(copy.FirstParameter()).Distance(bisector.EvalD0(first)) <= Precision.Confusion_s(), first
        assert bisector.FirstParameter() == pytest.approx(first, rel=1e-15, abs=1e-300)
