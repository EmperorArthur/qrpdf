import pytest

from qr_pdf.fpdf.template_helpers import frange


def test_frange_zero():
    """ Make sure frange behaves like range when given a bad value """
    with pytest.raises(ValueError) as v_error:
        frange(0, 10, 0)
        range(0, 10, 0)
    assert "must not be zero" in str(v_error.value)


@pytest.mark.parametrize("start, stop", [(0, 1), (1, 0), (1, 1), (0, 0), (0, 10)])
def test_frange_int_two(start: int, stop: int):
    """ Make sure frange matches the behavior of range for two numbers """
    fr_result = list(frange(start, stop))
    r_result = list(range(start, stop))
    assert fr_result == r_result


@pytest.mark.parametrize("start, stop, step", [(0, 1, 1), (1, 0, 1), (1, 1, 1), (0, 0, 1), (0, 10, 1), (0, 10, 2)])
def test_frange_int_three(start: int, stop: int, step: int):
    """ Make sure frange matches the behavior of range for three numbers """
    fr_result = list(frange(start, stop, step))
    r_result = list(range(start, stop, step))
    assert fr_result == r_result


def test_frange_simple_offset_start():
    fr_result = list(frange(0.1, 8.5, 0.5))
    assert fr_result == [0.1, 0.6, 1.1, 1.6, 2.1, 2.6, 3.1, 3.6, 4.1, 4.6, 5.1, 5.6, 6.1, 6.6, 7.1, 7.6, 8.1]


def test_frange_simple_zero_start():
    fr_result = list(frange(0, 8.5, 0.5))
    assert fr_result == [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]


def test_frange_include_last_no_difference():
    fr_result = list(frange(0.1, 8.5, 0.5, True))
    assert fr_result == [0.1, 0.6, 1.1, 1.6, 2.1, 2.6, 3.1, 3.6, 4.1, 4.6, 5.1, 5.6, 6.1, 6.6, 7.1, 7.6, 8.1]


def test_frange_include_last_extra():
    fr_result = list(frange(0.0, 8.5, 0.5, True))
    assert fr_result == [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5]
