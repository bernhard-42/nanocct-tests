# Translated from OCCT src/FoundationClasses/TKernel/GTests/OSD_PerfMeter_Test.cxx (LGPL-2.1 with the OCCT exception)
import math

import pytest

from nanocct.OSD import OSD_PerfMeter
from nanocct.TCollection import TCollection_AsciiString


@pytest.fixture(autouse=True)
def reset_all_meters():
    # OSD_PerfMeterTest::SetUp / TearDown
    OSD_PerfMeter.ResetALL_s()
    yield
    OSD_PerfMeter.ResetALL_s()


def do_some_work(time_in_sec=0.1):
    meter = OSD_PerfMeter("WorkMeter", True)
    while meter.Elapsed() < time_in_sec:
        result = 0.0
        for i in range(10000):
            result += math.sin(i * 0.001) * math.cos(i * 0.002)
            result += math.sqrt(i + 1.0)
            result += math.pow(i * 0.1, 1.5)

            a_str = TCollection_AsciiString("Test")
            a_str += TCollection_AsciiString(i)
            a_str.Length()
    meter.Kill()


def test_OSD_PerfMeterTest_BasicCreationWithAutoStart():
    meter = OSD_PerfMeter("TestMeter", True)
    do_some_work()
    meter.Stop()
    elapsed = meter.Elapsed()
    assert elapsed > 0.0


def test_OSD_PerfMeterTest_ManualStartStop():
    meter = OSD_PerfMeter("ManualMeter", False)
    meter.Start()
    do_some_work()
    meter.Stop()
    elapsed = meter.Elapsed()
    assert elapsed > 0.0


def test_OSD_PerfMeterTest_DefaultConstructorAndInit():
    meter = OSD_PerfMeter()
    meter.Init("InitializedMeter")
    meter.Start()
    do_some_work()
    meter.Stop()
    assert meter.Elapsed() > 0.0


def test_OSD_PerfMeterTest_SharedMetersByName():
    meter_name = "SharedMeter"

    meter1 = OSD_PerfMeter(meter_name)
    do_some_work()

    meter2 = OSD_PerfMeter()
    meter2.Init(meter_name)
    do_some_work()

    meter1.Stop()
    elapsed = meter1.Elapsed()
    assert elapsed > 0.0

    # Stopping meter2 has no effect: both share the meter meter1 already stopped
    meter2.Stop()
    elapsed2 = meter2.Elapsed()
    assert elapsed == elapsed2


def test_OSD_PerfMeterTest_RestartMeter():
    meter = OSD_PerfMeter("RestartMeter")
    do_some_work(0.1)
    meter.Stop()
    elapsed1 = meter.Elapsed()
    assert elapsed1 > 0.0

    meter.Start()
    do_some_work(0.2)
    meter.Stop()
    elapsed2 = meter.Elapsed()
    assert elapsed2 > 0.0

    assert elapsed1 != elapsed2


def test_OSD_PerfMeterTest_RelativeTimingAccuracy():
    meter1 = OSD_PerfMeter("ShortMeter")
    meter2 = OSD_PerfMeter("LongMeter")

    do_some_work(0.1)
    meter1.Stop()

    do_some_work(0.5)
    meter2.Stop()

    short_elapsed = meter1.Elapsed()
    long_elapsed = meter2.Elapsed()

    assert short_elapsed > 0.0
    assert long_elapsed > 0.0
    assert long_elapsed > short_elapsed


def test_OSD_PerfMeterTest_PrintALL():
    meter1 = OSD_PerfMeter("Meter1")
    do_some_work(0.1)
    meter1.Stop()

    meter2 = OSD_PerfMeter("Meter2")
    do_some_work(0.2)
    meter2.Stop()

    meter3 = OSD_PerfMeter("Meter3")
    do_some_work(0.3)
    meter3.Stop()

    output = OSD_PerfMeter.PrintALL_s().ToCString()

    assert "Meter1" in output
    assert "Meter2" in output
    assert "Meter3" in output


def test_OSD_PerfMeterTest_ResetALL():
    meter1 = OSD_PerfMeter("ResetMeter1")
    do_some_work(0.1)
    meter1.Stop()

    meter2 = OSD_PerfMeter("ResetMeter2")
    do_some_work(0.2)
    meter2.Stop()

    assert meter1.Elapsed() > 0.0
    assert meter2.Elapsed() > 0.0

    OSD_PerfMeter.ResetALL_s()

    assert meter1.Elapsed() == 0.0
    assert meter2.Elapsed() == 0.0


def test_OSD_PerfMeterTest_UnusedMeter():
    meter = OSD_PerfMeter("UnusedMeter", False)
    assert meter.Elapsed() == 0.0

    meter.Stop()
    assert meter.Elapsed() == 0.0


def test_OSD_PerfMeterTest_PrintMethod():
    meter_name = TCollection_AsciiString("PrintTestMeter")
    meter = OSD_PerfMeter(meter_name)

    do_some_work()
    meter.Stop()

    output = meter.Print().ToCString()

    assert meter_name.ToCString() in output
    assert any(ch in output for ch in "0123456789")
    assert "sec" in output


def test_OSD_PerfMeterTest_KillMethod():
    meter = OSD_PerfMeter("KillTestMeter")
    do_some_work()
    meter.Stop()

    elapsed = meter.Elapsed()
    assert elapsed > 0.0

    meter.Kill()

    elapsed_after_kill = meter.Elapsed()
    assert elapsed_after_kill == 0.0

    all_meters = OSD_PerfMeter.PrintALL_s().ToCString()
    assert "KillTestMeter" not in all_meters


def test_OSD_PerfMeterTest_KillRunningMeter():
    meter = OSD_PerfMeter("KillRunningMeter")

    meter.Kill()

    elapsed_after_kill = meter.Elapsed()
    assert elapsed_after_kill == 0.0

    meter.Init("KillRunningMeter")
    meter.Start()
    do_some_work()
    meter.Stop()

    assert meter.Elapsed() > 0.0
