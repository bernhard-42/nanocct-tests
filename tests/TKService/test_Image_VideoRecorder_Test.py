# Translated from OCCT src/Visualization/TKService/GTests/Image_VideoRecorder_Test.cxx (LGPL-2.1 with the OCCT exception)
# OpenVideoFile, InvalidParameters and WriteFrames are left out: their bodies are HAVE_FFMPEG-only and nanocct's OCCT is built with USE_FFMPEG=OFF.
import pytest

from nanocct.Image import Image_VideoParams, Image_VideoRecorder


@pytest.fixture
def recorder():
    rec = Image_VideoRecorder()
    yield rec
    rec.Close()


def test_Image_VideoRecorderTest_DefaultConstructor(recorder):
    assert recorder is not None
    assert recorder.FrameCount() == 0


def test_Image_VideoRecorderTest_VideoParamsStructure(recorder):
    params = Image_VideoParams()
    assert params.Width == 0
    assert params.Height == 0
    assert params.FpsNum == 0
    assert params.FpsDen == 1
    assert params.Format.IsEmpty()
    assert params.VideoCodec.IsEmpty()
    assert params.PixelFormat.IsEmpty()
    params.SetFramerate(30)
    assert params.FpsNum == 30
    assert params.FpsDen == 1
    params.SetFramerate(25, 2)
    assert params.FpsNum == 25
    assert params.FpsDen == 2


def test_Image_VideoRecorderTest_CloseWithoutOpen(recorder):
    recorder.Close()
    assert recorder.FrameCount() == 0
