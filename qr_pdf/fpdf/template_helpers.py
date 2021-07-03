""" Helper functions to make fpdf2 Templates more useful """

__author__ = "Arthur Moore <Arthur.Moore.git@cd-net.net>"
__copyright__ = "Copyright (C) 2021 Arthur Moore"
__license__ = "MIT"

from collections.abc import Sequence
from typing import Union, Tuple, Iterator

from fpdf.fpdf import get_page_format

from .helpers import convert_unit


class frange(Sequence):
    """
    Floating point range function, with the option of including the stop number if exactly reached
    """

    def __init__(self, start: float, stop: float, step: float = 1, include_stop: bool = False):
        """
        :param start: Starting Number
        :param stop: Maximum number
        :param step: Number to increment by
        :param include_stop: If the stop is reached exactly, if it will be included or not
        """
        if step == 0:
            raise ValueError("step must not be zero")
        self.start, self.stop, self.step = start, stop, step
        self.include_stop = include_stop
        pass

    def __getitem__(self, key: Union[int, slice]) -> Union[float, "frange"]:
        if isinstance(key, slice):
            return frange(self[slice.start], self[slice.stop], self.step)
        if key >= self.__len__():
            raise IndexError("index out of range")
        return self.step * key + self.start

    def __len__(self) -> int:
        out, remainder = divmod(self.stop - self.start, self.step)
        if remainder != 0:
            out += 1
        elif self.include_stop:
            out += 1
        return int(max(out, 0))

    def __str__(self):
        if self.step == 1 and not self.include_stop:
            return f"frange({self.start}, {self.stop})"
        elif not self.include_stop:
            return f"frange({self.start}, {self.stop}, {self.step})"
        return f"frange({self.start}, {self.stop}, {self.step}, {self.include_stop})"


def generate_grid_start_points(cell_size: Union[float, Tuple[float, float]],
                               margins: Union[float, Tuple[float, float, float, float]],
                               page_size: Tuple[float, float]
                               ) -> Iterator[Tuple[float, float]]:
    """
    Generate fpdf cell start points for a grid.  Upper left point of each cell.

    Use this with a size less than or equal to spacing to create cells.

    :param cell_size: The size of each row/column.  Either a single number or `(width, height)`
    :param margins: The page margins. Either a single number or `(left, top, right, bottom)`
    :param page_size: The size of the page to generate points for.
    :return Tuples in the **same unit** as given.
    """

    # Convert everything to a tuples
    if not isinstance(cell_size, (tuple, list)):
        cell_size = (cell_size, cell_size)
    if not isinstance(margins, (tuple, list)):
        margins = (margins, margins, margins, margins)

    # Generate the points (special handling is done so cells that exactly fit will work)
    x_starts = tuple(frange(margins[0], page_size[0] - margins[2] - cell_size[0], cell_size[0], True))
    y_starts = tuple(frange(margins[1], page_size[1] - margins[3] - cell_size[1], cell_size[1], True))

    for y in y_starts:
        for x in x_starts:
            yield x, y


def generate_element_grid(size: Union[float, Tuple[float, float]],
                          col_spacing: float, row_spacing: float,
                          margins: Union[float, Tuple[float, float, float, float]],
                          page_format: Union[str, Tuple[float, float]],
                          unit: str,
                          element_template: dict
                          ) -> Iterator[dict]:
    """
    Create a grid of elements for fpdf.Template
    :param size: The size of each element. Either a single number or `(width, height)`
    :param col_spacing: The empty space between each column
    :param row_spacing: The empty space between each row
    :param margins: The page margins (either a single number or `(left, top, right, bottom)`)
    :param page_format: Any page format string as accepted by `fpdf.get_page_format(...)` or a tuple of max page size
    :param unit: The units all other parameters are in. As accepted by `fpdf.FPDF`
    :param element_template: A copyable dict to be used for each element.
    :returns Elements for fpdf.Template, with points in mm.  Since, that's the only unit it accepts!
    """
    # Multiply by this to go from one unit to another
    unit_translation_factor = convert_unit(1, unit, "mm")
    # Make sure size is in the correct format
    if not isinstance(size, (tuple, list)):
        size = (size, size)
    width, height = size[0], size[1]
    page_size = convert_unit(get_page_format(page_format, k=1), 1, unit)

    points = generate_grid_start_points(cell_size=(width + col_spacing, height + row_spacing),
                                        margins=margins,
                                        page_size=page_size)
    # Convert to mm here
    width, height = width * unit_translation_factor, height * unit_translation_factor
    for i, (x, y) in enumerate(points):
        # This is O(n), but is simpler than doing all the conversions earlier
        x, y = x * unit_translation_factor, y * unit_translation_factor
        element = element_template.copy()
        element["name"] = element.get("name", "") + "_{}".format(i)
        element["x1"] = x
        element["y1"] = y
        element["x2"] = x + width
        element["y2"] = y + height
        yield element
