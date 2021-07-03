"""
MIT Licensed par2 parser

Par2 is a file format for using Reed-Solomon Coding to perform file recovery operations using "blocks" of recovery data.

Par2 is a great format, but is not optimized for this use case.
In addition, par2cmdline has at least one "gotcha" that this parser helped catch.

Pros:
* Everything is in "packets", with extremely easy to decode headers.
* Packet headers are easy to find, with their "magic" values ?guaranteed? to only show up there.
* Any amount of padding (including random data) is allowed between packets.
* Provided that enough redundancy exists, a missing file can be completely reconstructed.

Pain Points:
* CREATORPACKET is useful, but takes up space (may still be worth it)
* Recovery packets are really "Block Size" + 68, so to fit them in 512 chunks, `-s444` must be used.
  * This is not obvious or clearly documented.
* Every *.vol*+*.par2" file contains a copy of the blocks in "*.par2"
* Even if `-n1` is used to create a single file, both "*.par2" and "*.vol0+*.par2" files are created
* The `-r` switch does not accept values over 100%. (https://github.com/Parchive/par2cmdline/pull/158)

# Par2cmdline usage
This is based on the pain points identified above.
It creates a single file, with the correct recovery packet size, and then makes it the sole recovery file.
```
par2 create -s444 -n1 -v -v <in_file>
rm "<in_file>.par2"
mv "<in_file>.vol*.par2" "<in_file>.par2"
```
If you would like to adjust the amount of data that can be recovered, use the `-r` flag.

# References:
* Packet & Header format: https://github.com/Parchive/par2cmdline/blob/master/src/par2fileformat.h
* "magic" & "type"/"signature" values: https://github.com/Parchive/par2cmdline/blob/master/src/par2fileformat.cpp

Note that you can recover everything in the second link easily from any "vol...par2" file.
"""

__author__ = "Arthur Moore <Arthur.Moore.git@cd-net.net>"
__copyright__ = "Copyright (C) 2021 Arthur Moore"
__license__ = "MIT"

import re
import struct
import mmap
from collections.abc import Sized, Hashable
from hashlib import md5
from io import BufferedIOBase
from logging import getLogger
from pathlib import Path
from typing import NamedTuple, List, Union, Optional, Iterator, Tuple
from tarfile import BLOCKSIZE as TAR_BLOCK_SIZE

logger = getLogger()

MD5_FORMAT = "16s"

# These are the magic values Par2 uses to identify packets
PACKET_TYPES = {
    # Only one of these
    # size: header + 8 + 4 + (16 * <number_of_FileDescription/FileVerification_packets>)
    "Main": b'PAR 2.0\x00Main\x00\x00\x00\x00',
    # Only one of these
    # size: header + 4 + variable (Fixed per compiled program)
    "Creator": b'PAR 2.0\x00Creator\x00',
    # Number of files used to create the ".par2" file.
    # size: variable
    "FileDescription": b'PAR 2.0\x00FileDesc',
    # Same number as "FileDescription"
    # size: variable
    "FileVerification": b'PAR 2.0\x00IFSC\x00\x00\x00\x00',
    # size: header + 4 + Main.blocksize (Fixed at file creation)
    "RecoveryBlock": b'PAR 2.0\x00RecvSlic',
}

# Use for identifying packets
PACKET_LOOKUP = {value: key for key, value in PACKET_TYPES.items()}

# This is used so often, it's worth just defining it
PACKET_HEADER_SIZE = 64


# noinspection PyNamedTuple
class PacketHeader(NamedTuple):
    """ The header for every par2 packet """
    _format = "<" + "8s" + "Q" + MD5_FORMAT + MD5_FORMAT + "16s"
    _magic_expected = b'PAR2\x00PKT'
    magic: bytes  # Should always be b'PAR2\x00PKT'
    length: int  # Of entire packet (including header)
    hash: bytes  # md5 of entire packet. Excluding first 3 fields of header (32 bytes)
    set_id: bytes
    signature: bytes  # Should be in PACKET_TYPES.values()

    @classmethod
    def from_bytes(cls, data: bytes) -> "PacketHeader":
        """ Create from raw binary data """
        return cls._make(struct.unpack_from(cls._format, data))

    @classmethod
    def size_bytes(cls) -> int:
        """
        Get the size of data as bytes

        Useful for determining offsets and minimum data for `from_bytes`.
        """
        return struct.calcsize(cls._format)

    def is_valid(self) -> bool:
        """ If the header matches what it is supposed to (does not check hash) """
        return self.magic == self._magic_expected and \
               self.signature in PACKET_LOOKUP

    def as_bytes(self) -> bytes:
        return struct.pack(self._format, *self)

    @property
    def type(self) -> str:
        """ A human readable type of the packet the header is for """
        return PACKET_LOOKUP.get(self.signature, "Unknown")


class Packet(Sized, Hashable):
    """
    A Par2 Packet
    WARNING: Watch out for memory limitations with large data / many packets
    """

    def __init__(self, packet_type: str = "Unknown", set_id: bytes = b'', data: bytes = b'', **kwargs):
        """
        Create a new packet

        Accepts "header: PacketHeader" as a kwarg to bypass normal initialization
        """
        self._data_after_header: bytes = data
        if "header" in kwargs:
            self._header = kwargs["header"]
            return

        header = PacketHeader(magic=PacketHeader._magic_expected,
                              length=PACKET_HEADER_SIZE + len(data), hash=b'', set_id=set_id,
                              signature=PACKET_TYPES.get(packet_type, b''))
        self._header: PacketHeader = header  # Make sure someone knows what they're doing when writing to this
        self._header = self._header._replace(hash=self._generate_hash())

    def __repr__(self):
        return "Packet: {} - {} bytes".format(self.header.type, self.__len__())

    @classmethod
    def from_bytes(cls, data: Union[bytes, memoryview]) -> "Packet":
        """
        Read a packet from raw bytes.

        If fed a memoryview, then non-header data is kept that way.
        WARNING: Header data is never kept as a memoryview

        Internally handles all the variable sizing, so for offsets you can just do `...(data=buffer[offset:])`
        """
        header = PacketHeader.from_bytes(data)
        packet = cls(header=header, data=data[PACKET_HEADER_SIZE:header.length])
        return packet

    def _generate_hash(self) -> bytes:
        """ Generate the hash that should be in the header """
        return md5(self.as_bytes()[32:]).digest()

    def as_bytes(self) -> bytes:
        """
        Get the packet in the simplest way possible
        WARNING: Even if the packet was built from a memoryview, this still returns bytes.
        """
        return self.header.as_bytes() + self._data_after_header

    @property
    def header(self) -> PacketHeader:
        return self._header

    def is_valid(self) -> bool:
        """
        If the packet is (seems) valid

        Does not perform extensive internal checks, just basic matching to header
        """
        return self.header.is_valid() and \
               (len(self._data_after_header) + PACKET_HEADER_SIZE) == self.header.length and \
               (self._generate_hash() == self.header.hash)

    def __len__(self):
        """ The size of the entire packet (including header) """
        return self.header.length

    def __eq__(self, other: "Packet"):
        """
        Check if the other packet is the same (fast)

        This mostly just compares headers.  It assumes both are valid!
        """
        if not isinstance(other, self.__class__):
            return False
        return self.header == other.header

    def __hash__(self):
        return self.header.__hash__()


class CreatorPacket(Packet):
    def __init__(self, client: str = "", set_id: bytes = b'', **kwargs):
        if "header" in kwargs:
            super().__init__(**kwargs)
            return
        data = client.encode()
        padding = 4 - len(data) % 4
        data += b'\0' * padding
        super().__init__(packet_type="Creator", set_id=set_id, data=data)

    @classmethod
    def from_bytes(cls, data: Union[bytes, memoryview]) -> "CreatorPacket":
        out = super().from_bytes(data)
        if out.header.type != "Creator":
            raise ValueError("Decoded Packet is actually a {} Packet, not a Creator Packet".format(out.header.type))
        return out

    @property
    def client(self) -> str:
        """ Get the client encoded by the packet """
        return bytes(self._data_after_header).rstrip(b'\0').decode()


def get_packets(data: Union[bytes, memoryview], packet_type: Optional[str] = None) -> Iterator[Packet]:
    """
    Get all the packets of a particular type.  If no type is given, returns all packets.

    WARNING: packets are generated with non-header data as a `memoryview`.

    :param data: The data to search through.
    :param packet_type: The type of packet to look for. PACKET_TYPES.keys()
    """
    data = memoryview(data)
    packet_search = re.compile(PacketHeader._magic_expected)
    for match in packet_search.finditer(data):
        packet = Packet.from_bytes(data[match.start():])
        if packet_type is None or packet.header.type == packet_type:
            yield packet


def get_packet_unique(data: Union[bytes, memoryview], packet_type: str) -> Optional[Packet]:
    """
    Get all the packets of a particular type.  If no type is given, returns all packets.

    WARNING: packets are generated with non-header data as a `memoryview`.

    :param data: The data to search through.
    :param packet_type: The type of packet to look for. PACKET_TYPES.keys()
    """


def _get_unused_block_size(used: int):
    """
    Get how many bytes are remaining in the current block.

    This is trickier than it looks, since it accepts used numbers higher than 1 block.
    """
    used = used % TAR_BLOCK_SIZE
    if used == 0:
        return 0
    return TAR_BLOCK_SIZE - used


def _get_optimized_main(data: Union[bytearray, bytes, memoryview]) -> Tuple[bytes, Optional[CreatorPacket]]:
    """
    Get a Main packet optimized for use in tar files.
    This means it is padded/aligned to 512 bytes,
    and (if possible) the Creator and Main packets share a block.

    Otherwise, the Creator packet will be output separately for possible inclusion later.
    """
    creator_packets = list(get_packets(data, "Creator"))
    main_packets = list(get_packets(data, "Main"))

    # Verification
    if len(creator_packets) > 1:
        if all(packet == creator_packets[0] for packet in creator_packets):
            logger.info("Found {} duplicate Creator packets".format(len(creator_packets) - 1))
            creator_packets = [creator_packets[0]]
        else:
            raise ValueError("Found multiple ({}) different Creator packets.  Recovery file is suspect.".format(
                len(creator_packets)))
    if len(main_packets) > 1:
        if all(packet == main_packets[0] for packet in main_packets):
            logger.info("Found {} duplicate Main packets".format(len(main_packets) - 1))
            main_packets = [main_packets[0]]
        else:
            raise ValueError(
                "Found multiple ({}) different Main packets.  Recovery file is suspect.".format(len(main_packets)))
    if len(main_packets) < 1:
        raise ValueError("Main packet not found!")
    if len(creator_packets) < 1:
        from datetime import datetime
        date = datetime.now().date()
        creator_packets.append(CreatorPacket("qr-pdf on {}".format(date), main_packets[0].header.set_id))

    out = main_packets[0].as_bytes()
    creator_out = None
    bin_bytes_remaining = _get_unused_block_size(len(main_packets[0]))
    if bin_bytes_remaining >= len(creator_packets[0]):
        out += creator_packets[0].as_bytes()
        bin_bytes_remaining -= len(creator_packets[0])
    else:
        creator_out = creator_packets[0]
        logger.info("Not Enough Space to pack Creator packet with Main packet")
    out += b'\0' * bin_bytes_remaining
    return out, creator_out


def _get_optimized_file_data(data: Union[bytearray, bytes, memoryview]) -> bytes:
    """
    Get all the file packets optimized for use in tar files.
    This means everything is padded/aligned to 512 bytes,
    and (if possible) the Creator and Main packets share a block.

    WARNING: This produces a bytes object slightly greater than the index / hash information for all files.
    Which may be large!
    """
    out = b''
    # Extract "FileDescription" and "FileVerification" packets
    file_packets: List[Packet] = list(set(get_packets(data, "FileDescription")) |
                                      set(get_packets(data, "FileVerification")))
    # Use Bin Packing to optimally pack them using a variation of First Fit Decreasing and Best-Fit Algorithms
    # The differences are:
    # * Items are sorted as in First Fit Decreasing
    # * Some items may be larger than a single bin, and the remainder must be filled/packed immediately
    # * Write once, so only a single bin may be open at once
    # * Items may be skipped
    # https://en.wikipedia.org/wiki/Bin_packing_problem
    # Solution is:
    # * Sort the list (largest first)
    # * Each outer iteration packs a single bin with ot least one packet:
    #   * Move the largest remaining packet to a new bin
    #   * Iterate through all the remaining packets, moving them to the bin if possible
    #   * Close the bin
    # The outer iteration can pack multiple bins if a packet is too large for a single one.
    file_packets.sort(key=len, reverse=True)
    while len(file_packets):
        packet = file_packets.pop(0)  # Handle at least one packet per iteration
        out += packet.as_bytes()
        bin_bytes_remaining = _get_unused_block_size(len(packet))
        if bin_bytes_remaining <= PACKET_HEADER_SIZE:
            # Optimization. Nothing will fit, so close the bin
            out += b'\0' * bin_bytes_remaining
            continue
        to_drop = []  # Implementation detail, python lists should never be modified while being iterated through.
        for i, packet in enumerate(file_packets):
            # Only have to do this once to fill the bin
            if len(packet) <= bin_bytes_remaining:
                out += packet.as_bytes()
                bin_bytes_remaining -= len(packet)
                to_drop.append(i)
        for i in sorted(to_drop, reverse=True):
            del file_packets[i]  # drop from highest index down
        # All possible packets are written, so close the bin
        out += b'\0' * bin_bytes_remaining
    return out


def optimize_for_tar(in_file: Union[str, Path, bytearray, bytes], out: Union[str, Path, BufferedIOBase]):
    """
    Optimize a ".par2" file for use with tar.

    * Puts the most important data first and last.
    * "Main" -> File Packets (mixed) -> Recovery -> File Packets (mixed) -> "Main"
    * Makes sure the "Main" packet is either in its own 512 byte chunk(s) or with the "Creator" packet
    * "Creator" packet is dropped if it will not fit.
    * Packet(s) are padded to multiples of 512 bytes
    * Uses bin-packing and padding to optimize File Packets
    * The only packets that will span a 512 byte chunk are those larger than 512 bytes.

    Note: This assumes the file was generated with Recovery bin sizes >= 444 bytes (512 with packet data)
    """

    if isinstance(in_file, str):
        in_file = Path(in_file)
    if isinstance(in_file, Path):
        in_file_handle = in_file.open("rb")
        try:
            in_file = mmap.mmap(in_file_handle.fileno(), 0, access=mmap.ACCESS_READ)
        except mmap.error as e:
            in_file_handle.close()
            raise e

    if isinstance(out, str):
        out = Path(out)
    if not isinstance(out, BufferedIOBase):
        out = out.open("wb")

    written = 0

    # Get the Main / Creator packets and write one copy of Main at the start
    main_data, creator_packet = _get_optimized_main(in_file)
    written += out.write(main_data)

    # Get the file packets and write one copy at the start
    file_data = _get_optimized_file_data(in_file)
    written += out.write(file_data)
    header_block_size = (len(main_data) + len(file_data)) / TAR_BLOCK_SIZE
    assert int(header_block_size) == header_block_size, "Everything should be in terms of whole blcks"
    logger.info("Header takes {} blocks".format(int(header_block_size)))

    # Extract RecoveryBlock packets
    recovery_count = 0
    recovery_written = 0
    for packet in get_packets(in_file, "RecoveryBlock"):
        recovery_count += 1
        recovery_written += out.write(packet.as_bytes())
        # Never try to stuff recovery packets, and instead pad the current block
        bin_bytes_remaining = _get_unused_block_size(len(packet))
        recovery_written += out.write(b'\0' * bin_bytes_remaining)
    written += recovery_written
    logger.info("Wrote {} Recovery packets in {} blocks".format(recovery_count, int(recovery_written / TAR_BLOCK_SIZE)))
    # if creator_packet is not None:
    #     out.write(creator_packet.as_bytes())
    written += out.write(file_data)
    written += out.write(main_data)
    logger.info("Wrote {} blocks total".format(int(written / TAR_BLOCK_SIZE)))
