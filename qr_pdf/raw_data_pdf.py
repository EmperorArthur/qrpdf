from collections import Mapping
from typing import Tuple, Union, List, Iterator

from fpdf import FPDF, Template

import qrcode

from .fpdf.helpers import get_scale_factor, convert_unit
from .fpdf.template_helpers import generate_grid_start_points
from .fpdf.qr import qr_handler


class RawDataPDF:
    """
    A wrapper for generating PDFs holding QR codes with raw data
    """

    BASE_QR_TEMPLATE = {
        "name": "barcode_{}",
        "type": "QR",
        "priority": 0,
        "text": None,
        "box_size": 2,
        "border": 0,
        "error_correction": qrcode.ERROR_CORRECT_Q
    }
    BASE_TEXT_TEMPLATE = {
        "name": "text_{}",
        "type": "T",
        "priority": 0,
        "text": None,
        "align": "C",
        "size": 10
    }

    def __init__(self, pdf=None, qr_physical_size=2, **kwargs):
        """

        :param pdf:
        :param qr_physical_size:
        :param kwargs:
        """
        if pdf is None:
            self.pdf = FPDF(**kwargs)
        self.qr_physical_size = qr_physical_size
        self.column_spacing = 0.1
        self.row_spacing = 0.1
        self.qr_template = self.BASE_QR_TEMPLATE.copy()
        self.text_template = self.BASE_TEXT_TEMPLATE.copy()

    def _generate_grid_start_points(self, cell_size: Union[float, Tuple[float, float]]) -> Iterator[Tuple[float, float]]:
        """
        Same as the normal `generate_grid_start_points`, but uses self.pdf for everything but cell_size
        :param cell_size: The cell size **in the same unit as the PDF is in**
        :return:
        """
        return generate_grid_start_points(cell_size=cell_size,
                                          margins=(self.pdf.l_margin, self.pdf.t_margin,
                                                   self.pdf.r_margin, self.pdf.b_margin),
                                          page_size=(self.pdf.w, self.pdf.h))

    def generate_qr_page_elements(self, qr_template, text_template=None) -> Iterator[List[dict]]:
        """
        Generate a template for QR codes on a page.

        Takes page format, margin, and unit information from the internal FPDF file.
        If no text_template is provided, then elements to place text under the QR codes are not generated.

        :param qr_template: Template to use to generate QR codes
        :param text_template: Template to use to generate the text under the QR codes (optional)
        :return:
        """
        text_height = 0
        if text_template is not None:
            text_height = text_template.get("size", 0) / self.pdf.k

        # Multiply by this to go from one unit to another
        unit_translation_factor = convert_unit(1, self.pdf.k, "mm")

        points = self._generate_grid_start_points(
            cell_size=(self.qr_physical_size + self.column_spacing,
                       self.qr_physical_size + self.row_spacing + text_height))

        for i, (x, y) in enumerate(points):
            # This is O(n), but is simpler than doing all the conversions earlier
            element = qr_template.copy()
            element["name"] = element.get("name", "barcode_{}").format(i)
            element["x1"] = x * unit_translation_factor
            element["y1"] = y * unit_translation_factor
            element["x2"] = (x + self.qr_physical_size) * unit_translation_factor
            element["y2"] = (y + self.qr_physical_size) * unit_translation_factor
            yield element
            if not text_height:
                continue
            element = text_template.copy()
            element["name"] = element.get("name", "text_{}").format(i)
            element["x1"] = x * unit_translation_factor
            element["y1"] = (y + self.qr_physical_size) * unit_translation_factor
            element["x2"] = (x + self.qr_physical_size) * unit_translation_factor
            element["y2"] = (y + self.qr_physical_size + text_height) * unit_translation_factor
            yield element

    def get_elements_per_page(self, include_text=False) -> int:
        """
        How many QR Codes can fit on a single page
        :param include_text: If each QR code should have text below it or not
        :return:
        """
        if include_text:
            return int(len(list(self.generate_qr_page_elements(self.qr_template, self.text_template)))  / 2)
        return len(list(self.generate_qr_page_elements(self.qr_template)))

    def add_data_page(self, data: Union[Mapping, list]):
        """
        Add a page of data.

        If data is a dict, then, each QR code will have the key displayed below it.
        If data is a list, then only the QR codes will be displayed

        :param data:
        :return:
        """
        qr_key = self.qr_template["name"]
        text_key = self.text_template["name"]

        if isinstance(data, Mapping):
            is_mapping = True
            elements = list(self.generate_qr_page_elements(self.qr_template, self.text_template))
            max_data = int(len(elements) / 2)
        else:
            is_mapping = False
            elements = list(self.generate_qr_page_elements(self.qr_template))
            max_data = len(elements)

        if len(data) > max_data:
            raise ValueError("A data page may only contain {} elements".format(max_data))

        template = Template(elements=elements)
        template.pdf = self.pdf
        template.handlers["QR"] = qr_handler
        template.add_page()
        if is_mapping:
            for i, (key, value) in enumerate(data.items()):
                template.texts[1][text_key.format(i)] = key
                template.texts[1][qr_key.format(i)] = value
        else:
            for i, value in enumerate(data):
                template.texts[1][qr_key.format(i)] = value

        # Need to adjust the PDF to work in mm, since that's all Template supports
        original_k = self.pdf.k
        self.pdf.k = get_scale_factor("mm")
        template.render()
        self.pdf.k = original_k
