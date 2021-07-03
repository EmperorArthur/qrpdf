from collections.abc import Iterator

import pytest

from qr_pdf.fpdf.template_helpers import generate_grid_start_points, frange


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


def test_generate_grid_start_points_returns_iterator():
    points = generate_grid_start_points(1, 10, 10)
    assert isinstance(points, Iterator)


def test_create_simple_grid_points():
    points = generate_grid_start_points(1, 10, 10)
    points = list(points)
    assert points == [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (0, 1), (1, 1),
                      (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1), (0, 2), (1, 2), (2, 2), (3, 2),
                      (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3),
                      (6, 3), (7, 3), (8, 3), (9, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4),
                      (8, 4), (9, 4), (0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5),
                      (0, 6), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (0, 7), (1, 7),
                      (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7), (0, 8), (1, 8), (2, 8), (3, 8),
                      (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8), (0, 9), (1, 9), (2, 9), (3, 9), (4, 9), (5, 9),
                      (6, 9), (7, 9), (8, 9), (9, 9)]


def test_create_grid_points_simple_margins():
    points = generate_grid_start_points(1, 8, 8, 1, 1)
    points = list(points)
    assert points == [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (1, 2), (2, 2), (3, 2), (4, 2),
                      (5, 2), (6, 2), (7, 2), (8, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3),
                      (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (1, 5), (2, 5), (3, 5), (4, 5),
                      (5, 5), (6, 5), (7, 5), (8, 5), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6),
                      (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (1, 8), (2, 8), (3, 8), (4, 8),
                      (5, 8), (6, 8), (7, 8), (8, 8)]


def test_create_grid_points_letter_margins_int():
    """
    A more real test, where a cell would have 0.5 to margin on the right hand side, and 0 on the bottom.
    Letter paper with 1in margins
    """
    points = generate_grid_start_points(1, 6.5, 9, 1, 1)
    points = list(points)
    assert points == [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2),
                      (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4),
                      (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6),
                      (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8),
                      (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9)]


def test_create_grid_points_letter_margins_larger_cell():
    """
    A more real test, where a cell would have 0.5 to margin on the right hand side, and 0 on the bottom.
    Letter paper with 1in margins
    """
    points = generate_grid_start_points(1.5, 6.5, 9, 1, 1)
    points = list(points)
    assert points == [(1.0, 1.0), (2.5, 1.0), (4.0, 1.0), (5.5, 1.0), (1.0, 2.5), (2.5, 2.5), (4.0, 2.5), (5.5, 2.5),
                      (1.0, 4.0), (2.5, 4.0), (4.0, 4.0), (5.5, 4.0), (1.0, 5.5), (2.5, 5.5), (4.0, 5.5), (5.5, 5.5),
                      (1.0, 7.0), (2.5, 7.0), (4.0, 7.0), (5.5, 7.0), (1.0, 8.5), (2.5, 8.5), (4.0, 8.5), (5.5, 8.5)]


def test_create_grid_points_letter_smaller_margins():
    """
    A more real test, where a cell would have 0.5 to margin on the right hand side, and 0.5 on the bottom.
    Letter paper with 0.5in margins
    """
    points = generate_grid_start_points(1, 7.5, 10, 0.5, 0.5)
    points = list(points)
    assert points == [(0.5, 0.5), (1.5, 0.5), (2.5, 0.5), (3.5, 0.5), (4.5, 0.5), (5.5, 0.5), (6.5, 0.5), (0.5, 1.5),
                      (1.5, 1.5), (2.5, 1.5), (3.5, 1.5), (4.5, 1.5), (5.5, 1.5), (6.5, 1.5), (0.5, 2.5), (1.5, 2.5),
                      (2.5, 2.5), (3.5, 2.5), (4.5, 2.5), (5.5, 2.5), (6.5, 2.5), (0.5, 3.5), (1.5, 3.5), (2.5, 3.5),
                      (3.5, 3.5), (4.5, 3.5), (5.5, 3.5), (6.5, 3.5), (0.5, 4.5), (1.5, 4.5), (2.5, 4.5), (3.5, 4.5),
                      (4.5, 4.5), (5.5, 4.5), (6.5, 4.5), (0.5, 5.5), (1.5, 5.5), (2.5, 5.5), (3.5, 5.5), (4.5, 5.5),
                      (5.5, 5.5), (6.5, 5.5), (0.5, 6.5), (1.5, 6.5), (2.5, 6.5), (3.5, 6.5), (4.5, 6.5), (5.5, 6.5),
                      (6.5, 6.5), (0.5, 7.5), (1.5, 7.5), (2.5, 7.5), (3.5, 7.5), (4.5, 7.5), (5.5, 7.5), (6.5, 7.5),
                      (0.5, 8.5), (1.5, 8.5), (2.5, 8.5), (3.5, 8.5), (4.5, 8.5), (5.5, 8.5), (6.5, 8.5), (0.5, 9.5),
                      (1.5, 9.5), (2.5, 9.5), (3.5, 9.5), (4.5, 9.5), (5.5, 9.5), (6.5, 9.5)]
