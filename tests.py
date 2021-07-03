
import logging
from pprint import pprint
from io import BytesIO
from qr_pdf.par2 import *

logging.basicConfig(level=logging.DEBUG)

with open("templated4.pdf.par2", "rb") as f:
    par_raw = f.read()

packets = list(get_packets(par_raw))
cp = packets[-1]
cp = CreatorPacket.from_bytes(bytes(cp))

sp = set(packets)
optimized = BytesIO()

optimize_for_tar("templated4.pdf.par2", "test.par2")