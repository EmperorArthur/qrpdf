"""
Provides a method for qrcode to directly write to / create an FPDF document.
"""

__author__ = "Arthur Moore <Arthur.Moore.git@cd-net.net>"
__copyright__ = "Copyright (C) 2021 Arthur Moore"
__license__ = "MIT"

from fpdf import FPDF
from qrcode.image.base import BaseImage


class FpdfImage(BaseImage):
    """
    qrcode image builder for FPDF.

    Provides a method for qrcode to directly write to / create an FPDF document.

    :example:
    ```
    pdf = qrcode.make("QR Data", image_factory=BaseImage)
    ```

    :example:
    ```

    pdf = FPDF()
    qr = qrcode.QRCode(image_factory=BaseImage)
    pdf.add_page()
    qr.add_data("Page 1")
    qr.make_image(pdf=pdf)
    qr.clear()
    qr.add_page()
    qr.make_image("Page 2")

    ```

    Note: This ignores things like "border".
    """

    def save(self, stream, kind=None):
        assert isinstance(self._img, FPDF)
        self._img.output(stream)

    def new_image(self, pdf: FPDF = None):
        """
        Create a new "image"
        :param pdf: The PDF to write to
        :return:
        """
        if pdf is None:
            pdf = FPDF(unit="pt")
            pdf.add_page()
        return pdf

    def drawrect(self, row, col):
        """ Directly draw a rect on the PDF """
        box = self.pixel_box(row, col)
        self._img.rect(box[0][0], box[0][1], self.box_size, self.box_size, style="DF")
