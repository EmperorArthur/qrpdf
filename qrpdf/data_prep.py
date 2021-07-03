from hashlib import sha256
from io import BytesIO
from tarfile import TarFile, PAX_FORMAT, TarInfo, GNU_FORMAT

data = {
    "file_name": "test",
    "compression": None,
    "split_method": "par2"
}

# Cover page per file
# Text
# Tar pax_headers

tarfile_contents = [
    "file",
    "file.sha256",
    "par2 file(s)"
]


def get_tarfile(filename):
    """ Get a tarfile with the above contents """
    hasher = sha256()
    with open(filename, "rb") as file:
        hasher.update(file.read())
    hash = hasher.hexdigest()
    hash_buffer = BytesIO(hash.encode())

    tar_buffer = BytesIO()
    tar_file = TarFile(mode='w', fileobj=tar_buffer, format=GNU_FORMAT)
    hash_info = TarInfo(filename + ".sha256")
    hash_info.size = len(hash_buffer.getvalue())
    tar_file.addfile(hash_info, hash_buffer)

    ["par2.exe", "create", "-s512", "-n1", "-v", "-v", filename]