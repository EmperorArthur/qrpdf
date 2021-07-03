""" Helper functions to make fpdf2 more useful """

__author__ = "Arthur Moore <Arthur.Moore.git@cd-net.net>"
__copyright__ = "Copyright (C) 2021 Arthur Moore"
__license__ = "MIT"

from typing import Union, Iterable, Dict

# These are the numbers used by fpdf. Assumes 72 dpi
FPDF_UNITS: Dict[str, float] = {
    "pt": 1.0,
    "mm": 72 / 25.4,
    "cm": 72 / 2.54,
    "in": 72.0,
}


def get_scale_factor(unit: Union[str, float]) -> float:
    """
    Get how many pts are in a unit.
    :param unit: A unit accepted by fpdf.FPDF
    :return: The number of points in that unit
    :raises FPDFException
    """
    if isinstance(unit, (int, float)):
        return float(unit)
    k = FPDF_UNITS.get(unit, None)
    if k is None:
        raise ValueError(f"Unit does not exist: {unit}")
    return k


def convert_unit(
        to_convert: Union[float, int, Iterable[Union[float, int, Iterable]]],
        old_unit: Union[str, float, int], new_unit: Union[str, float, int]
) -> Union[float, tuple]:
    """
    Convert a number or sequence of numbers from one unit to another.

    :param to_convert: The number / sequence of numbers, or points, to convert
    :param old_unit: A unit accepted by fpdf.FPDF or a number
    :param new_unit: A unit accepted by fpdf.FPDF or a number
    :return: to_convert converted from old_unit to new_unit or a tuple of the same
    """
    unit_conversion_factor = get_scale_factor(new_unit) / get_scale_factor(old_unit)
    if isinstance(to_convert, Iterable):
        return tuple(
            map(lambda i: convert_unit(i, 1, unit_conversion_factor), to_convert)
        )
    return to_convert / unit_conversion_factor
