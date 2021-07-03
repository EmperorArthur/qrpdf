# Create PDF files

from fpdf import FPDF, Template
import qrcode

from qr_pdf.fpdf.qr import qr_handler
from qr_pdf.fpdf.template_helpers import generate_element_grid
from qr_pdf.raw_data_pdf import RawDataPDF

ipsum = """Contrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.

The standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form, accompanied by English versions from the 1914 translation by H. Rackham."""

ipsum_a5 = ipsum[0:512]
ipsum_k = ipsum.encode()[0:1024]

# get_template_elements(2, 2.5, 2.5, 1, 'letter', unit="in")
# generate_grid_start_points(2.5, 0.5, 'letter', unit="in")


def create_helped_templated_pdf_1k_packed():
    """
    Tuned for 16/20 1k elements

    1024 bytes is 141x141 modules per QR code at 2in / code = 70.5 modules/inch
    """
    rd_pdf = RawDataPDF(unit="in", format="letter")
    rd_pdf.pdf.set_margins(0.1, 0.1, 0)
    rd_pdf.pdf.b_margin = 0
    rd_pdf.row_spacing = 0.05
    rd_pdf.text_template["size"] = 8
    rd_pdf.qr_physical_size = 2
    data = [ipsum_k] * rd_pdf.get_elements_per_page(True)
    dict_data = {"ipsum_{}".format(i): v for i, v in enumerate(data)}
    rd_pdf.add_data_page(dict_data)
    rd_pdf.pdf.output('templated_1k.pdf')


def create_helped_templated_pdf_512_packed():
    """
    Tuned for ???/63 512 byte elements
    While it is more data, the key benefit is tar writes data in 512 chunks.

    512 bytes is 105x105 modules per QR Code at 1in per code = 105 modules/inch

    """
    rd_pdf = RawDataPDF(unit="in", format="letter")
    rd_pdf.pdf.set_margins(0.4, 0.25, 0.4)
    rd_pdf.pdf.b_margin = 0.25
    rd_pdf.row_spacing = 0.05
    rd_pdf.text_template["size"] = 8
    rd_pdf.qr_physical_size = 1
    data = [ipsum_a5] * rd_pdf.get_elements_per_page(True)
    dict_data = {"ipsum_{}".format(i): v for i, v in enumerate(data)}
    rd_pdf.add_data_page(dict_data)
    rd_pdf.pdf.output('templated4.pdf')


def create_helped_templated_pdf_512_larger():
    """
    Tuned for ???/63 512 byte elements
    While it is more data, the key benefit is tar writes data in 512 chunks.

    512 bytes is 105x105 modules per QR Code at 1in per code = 105 modules/inch

    """
    rd_pdf = RawDataPDF(unit="in", format="letter")
    rd_pdf.pdf.set_margins(0.5, 0.25, 0.25)
    rd_pdf.pdf.b_margin = 0.25
    rd_pdf.row_spacing = 0.05
    rd_pdf.text_template["size"] = 8
    rd_pdf.qr_physical_size = 1.5
    data = [ipsum_a5] * rd_pdf.get_elements_per_page(True)
    dict_data = {"ipsum_{}".format(i): v for i, v in enumerate(data)}
    rd_pdf.add_data_page(dict_data)
    rd_pdf.pdf.output('template_512_larger.pdf')


def create_helped_templated_pdf():
    qr_template = {
        "name": "barcode",
        "type": "QR",
        "priority": 0,
        "text": ipsum.encode()[0:1023],
        "box_size": 2,
        "border": 0,
        "error_correction": qrcode.ERROR_CORRECT_Q
    }
    element_grid = generate_element_grid(2, 0.1, 0.1, (0.1, 0.5, 0, 0), "letter", "in", qr_template)
    pdf = Template(format="letter", elements=list(element_grid))
    pdf.handlers["QR"] = qr_handler
    pdf.add_page()
    # for key in pdf.keys:
        # pdf[key] = qr.make_image().get_image()
        # pdf.texts[1][key] = qr.make_image().get_image()
    # FIXME:  Issue with Template.__setitem__
    pdf.render('templated2.pdf')


def create_templated_pdf():
    """"""
    # Assumes inches are used on letter paper
    barcode_page_elements = []
    # x_starts = [1, 3.5, 6]
    # x_starts = [0.25, 2.5, 4.75, 7]
    # x_starts = [0.25, 2.25, 4.25, 6.25]
    x_starts = [0.1, 2.2, 4.3, 6.4]
    # y_starts = [1, 3.25, 5.5, 7.75]
    y_starts = [0.5, 2.6, 4.7, 6.8, 8.9]
    for xn, x in enumerate(x_starts):
        for yn, y in enumerate(y_starts):
            barcode_element = {
                "name": "barcode_{}_{}".format(xn, yn),
                "type": "I",
                "x1": x,
                "y1": y,
                "x2": x + 2,
                "y2": y + 2,
                "priority": 0,
                "text": None,
            }
            barcode_page_elements.append(barcode_element)

    pdf = Template(format="letter", elements=barcode_page_elements)
    pdf.pdf.k = 72.0  # Same as setting unit="in"
    pdf.add_page()
    qr = qrcode.QRCode(box_size=2, border=0, error_correction=qrcode.ERROR_CORRECT_Q)
    qr.add_data(ipsum.encode()[0:1023])
    for key in pdf.keys:
        # pdf[key] = qr.make_image().get_image()
        pdf.texts[1][key] = qr.make_image().get_image()
    # FIXME:  Issue with Template.__setitem__
    pdf.render('templated.pdf')


def direct_draw_pdf():
    from qr_pdf.qrcode_image_fpdf import FpdfImage
    pdf = FPDF(orientation="portrait", unit="in", format="letter")
    pdf.add_page()
    qr = qrcode.QRCode(box_size=2, border=0, error_correction=qrcode.ERROR_CORRECT_Q)
    qr.add_data("test")
    img = qr.make_image(image_factory=FpdfImage, pdf=pdf)
    img.get_image().output("test.pdf")


def create_pdf_image():
    pdf = FPDF(orientation="portrait", unit="pt", format="letter")
    pdf.add_page()
    qr = qrcode.QRCode(box_size=3, border=0, error_correction=qrcode.ERROR_CORRECT_Q)
    qr.add_data("test")
    img = qr.make_image()
    pdf.image(img.get_image())
    pdf.output("qrcode.pdf")


def add_mono_font(pdf: FPDF):
    from pymupdf_fonts import FiraMono_Regular as Font
    from tempfile import NamedTemporaryFile, TemporaryDirectory
    from pathlib import Path

    temp_dir = TemporaryDirectory(dir=str(Path().absolute()))
    font_file = NamedTemporaryFile(dir=temp_dir.name, delete=False)
    font_file.write(Font.fontbuffer)
    font_file.close()
    pdf.add_font(Font.fontdescriptor["name"], fname=font_file.name, uni=True)


def create_pdf_ascii():
    import io

    pdf = FPDF(orientation="portrait", unit="in", format="letter")
    add_mono_font(pdf)
    pdf.set_font('space mono regular')
    pdf.add_page()
    qr = qrcode.QRCode()
    qr.add_data("test")
    buffer = io.StringIO()
    qr.print_ascii(buffer)
    pdf.multi_cell(0, txt=buffer.getvalue())
    pdf.output("qrcode_ascii.pdf")


if __name__ == '__main__':
    print("main")
    # create_pdf()
