from inspect import signature
from typing import Optional, Any, NamedTuple

import qrcode
from fpdf import FPDF
from qrcode.image.base import BaseImage
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from typing_extensions import Literal

# The arguments that qrcode.QRCode accepts
QRCODE_KWARGS = set(signature(qrcode.QRCode).parameters.keys())


class QrElement(NamedTuple):
    name: str
    text: Any
    type: str = "QR"  # DO NOT CHANGE THIS
    priority: int = 0
    version: Optional[int] = None
    error_correction: Literal[ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H] = ERROR_CORRECT_M
    box_size: int = 10
    border:int = 4
    image_factory: Optional[BaseImage] = None
    mask_pattern: Optional[int] = None

    @property
    def type(self):
        return "QR"


def qr_handler(pdf: FPDF, *_, x1=0, y1=0, x2=0, y2=0, text="", **kwargs):
    """ fpdf.Template Handler for QR codes """
    if text:
        filtered_kwargs = {key:value for key, value in kwargs.items() if key in QRCODE_KWARGS}
        pdf.image(qrcode.make(data=text, **filtered_kwargs).get_image(), x1, y1, w=x2 - x1, h=y2 - y1, link="")
