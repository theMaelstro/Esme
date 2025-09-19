"""Read Binary Data from a File"""
import struct
from binary_reader import BinaryReader
import dataclasses

def decompress(save_data: bytes) -> bytes:
    """Decompress binary."""
    br = BinaryReader(save_data, encoding='sjis')
    header = br.read_bytes(16)

    output_string = bytearray()
    counters = []
    while br.eof() is False:
        byte = br.read_bytes(1)

        if byte == b'\x00':
            # Read the number of additional null bytes
            null_count_byte = br.read_bytes(1)
            null_count = int.from_bytes(null_count_byte, byteorder='little')

            counters.append(null_count)
            for _ in range(null_count):
                output_string.extend(b'\x00')

        else:
            output_string.extend(byte)

    #print(counters)
    return bytes(output_string)

def compress(save_data: bytes) -> bytes:
    """Compress binary."""
    output_string = bytearray()
    output_string.extend(b'\x63\x6d\x70\x20\x32\x30\x31\x31\x30\x31\x31\x33\x20\x20\x20\x00')

    br = BinaryReader(save_data)
    while br.eof() is False:
        byte = br.read_bytes(1)
        if byte == b'\x00':
            null_count = 1
            while br.eof() is False:
                byte = br.read_bytes(1)
                if byte != b'\x00':
                    output_string.extend(b'\x00')
                    output_string.extend(null_count.to_bytes(1))
                    output_string.extend(byte)
                    null_count = 0
                    break
                elif null_count == 255:
                    output_string.extend(b'\x00')
                    output_string.extend(null_count.to_bytes(1))
                    null_count = 0

                null_count += 1
            if br.eof() and null_count > 0:
                output_string.extend(b'\x00')
                output_string.extend(null_count.to_bytes(1))
        else:
            output_string.extend(byte)
    return bytes(output_string)

@dataclasses.dataclass
class BinaryFile:
    """Class representing single binary file with its mapped name."""
    file_data: bytes
    file_name: str

class SaveData:
    """
    Save Binary Data.
    """
    def __init__(
        self,
        savedata: bytes = 'b\00',
        decomyset: bytes = 'b\00',
        hunternavi: bytes = 'b\00',
        otomoairou: bytes = 'b\00',
        partner: bytes = 'b\00',
        platebox: bytes = 'b\00',
        platedata: bytes = 'b\00',
        platemyset: bytes = 'b\00',
        rengokudata: bytes = 'b\00',
        savemercenary: bytes = 'b\00',
        skinhist: bytes = 'b\00',
        minidata: bytes = 'b\00',
        scenariodata: bytes = 'b\00',
        savefavoritequest: bytes = 'b\00'
    ):
        self.savedata = BinaryFile(savedata, "savedata")
        self.decomyset = BinaryFile(decomyset, "decomyset")
        self.hunternavi = BinaryFile(hunternavi, "hunternavi")
        self.otomoairou = BinaryFile(otomoairou, "otomoairou")
        self.partner = BinaryFile(partner, "partner")
        self.platebox = BinaryFile(platebox, "platebox")
        self.platedata = BinaryFile(platedata, "platedata")
        self.platemyset = BinaryFile(platemyset, "platemyset")
        self.rengokudata = BinaryFile(rengokudata, "rengokudata")
        self.savemercenary = BinaryFile(savemercenary, "savemercenary")
        self.skinhist = BinaryFile(skinhist, "skinhist")
        self.minidata = BinaryFile(minidata, "minidata")
        self.scenariodata = BinaryFile(scenariodata, "scenariodata")
        self.savefavoritequest = BinaryFile(savefavoritequest, "savefavoritequest")

    @property
    def files(
        self
    ) -> tuple[BinaryFile, ...]:
        """The save_data property."""
        return (
            self.savedata,
            self.decomyset,
            self.hunternavi,
            self.otomoairou,
            self.partner,
            self.platebox,
            self.platedata,
            self.platemyset,
            self.rengokudata,
            self.savemercenary,
            self.skinhist,
            self.minidata,
            self.scenariodata,
            self.savefavoritequest
        )

class CharacterData:
    """
    Character Binary Data.
    """
    def __init__(
        self,
        save_data: bytes
    ):
        self.__save_data = save_data

    @property
    def save_data(
        self
    ) -> bytes:
        """The save_data property."""
        return self.__save_data

    def get_name(
        self
    ) -> str:
        """Get character name as string."""
        br = BinaryReader(self.__save_data)
        br.seek(0x58)
        raw_data = br.read_str(12, 'sjis')
        return raw_data

    def set_name(
        self,
        new_name: str
    ):
        """Write name to binary and return buffer."""
        br = BinaryReader(self.__save_data)
        br.seek(0x58)
        br.write_str_fixed(new_name, 12, 'sjis')
        self.__save_data = bytes(br.buffer())

    def get_keyflag(
        self
    ) -> str:
        """Get keyflag name as string."""
        br = BinaryReader(self.__save_data)
        br.seek(0x23D20)
        raw_data = br.read_bytes(8)
        #print("Raw data read:", raw_data)
        hex_data = raw_data.hex()
        #print("Hex representation:", hex_data)
        bin_data = bytes.fromhex(hex_data)
        return hex_data

    def set_keyflag(
        self,
        new_flag: str
    ):
        """Write keyflag to binary and return buffer."""
        br = BinaryReader(self.__save_data)
        br.seek(0x23D20)
        br.write_bytes(bytes.fromhex(new_flag))
        self.__save_data = bytes(br.buffer())

    def get_gender(
        self
    ) -> bytes:
        """Get character gender."""
        br = BinaryReader(self.__save_data)
        br.seek(0x50)
        raw_data = br.read_bytes(1)
        return struct.unpack('?',raw_data)[0]

    def get_zenny(
        self
    ) -> bytes:
        """Get character zenny."""
        br = BinaryReader(self.__save_data)
        br.seek(0xB0)
        raw_data = br.read_uint32()
        return raw_data

    def get_gzenny(
        self
    ) -> bytes:
        """Get character gzenny."""
        br = BinaryReader(self.__save_data)
        br.seek(0x1FF64)
        raw_data = br.read_uint32()
        return raw_data

    def get_cp(
        self
    ) -> bytes:
        """Get character cp."""
        br = BinaryReader(self.__save_data)
        br.seek(0x212E4)
        raw_data = br.read_uint32()
        return raw_data
