from enum import Enum
import struct

__all__ = [
    'ParseException',
    'ClassInfo',
    'ClassTypeInfo',
    'MemberTypeInfo',
    'Record',
    'RecordTypeEnumeration',
    'BinaryTypeEnumeration',
    'PrimitiveTypeEnumeration',
    'BinaryObjectString',
    'SerializationHeaderRecord',
    'ClassWithMembersAndTypes',
    'MessageEnd',
    'BinaryLibrary',
    'SerializedMessage',
]


def _read_enum(stream):
    data = stream.read(1)
    return struct.unpack("b", data)[0]


def _read_int32(stream):
    data = stream.read(4)
    return struct.unpack("<i", data)[0]


def _read_uint32(stream):
    data = stream.read(4)
    return struct.unpack("<I", data)[0]


def _read_lpstr(stream):
    str_len = 0

    while True:
        new_byte = int.from_bytes(stream.read(1), byteorder="little")
        str_len = (str_len << 7) + (new_byte & ~0x80)

        if new_byte & 0x80 == 0:
            break

    return stream.read(str_len).decode("utf-8")


class ParseException(Exception):
    pass


class RecordTypeEnumeration(Enum):
    SerializedStreamHeader = 0
    ClassWithId = 1
    SystemClassWithMembers = 2
    ClassWithMembers = 3
    SystemClassWithMembersAndTypes = 4
    ClassWithMembersAndTypes = 5
    BinaryObjectString = 6
    BinaryArray = 7
    MemberPrimitiveTyped = 8
    MemberReference = 9
    ObjectNull = 10
    MessageEnd = 11
    BinaryLibrary = 12
    ObjectNullMultiple256 = 13
    ObjectNullMultiple = 14
    ArraySinglePrimitive = 15
    ArraySingleObject = 16
    ArraySingleString = 17
    MethodCall = 21
    MethodReturn = 22


class BinaryTypeEnumeration(Enum):
    Primitive = 0
    String = 1
    Object = 2
    SystemClass = 3
    Class = 4
    ObjectArray = 5
    StringArray = 6
    PrimitiveArray = 7

    def has_additional_info(self):
        if self == self.Primitive:
            return True

        if self == self.PrimitiveArray:
            return True

        if self == self.SystemClass:
            return True

        if self == self.Class:
            return True

        return False


class PrimitiveTypeEnumeration(Enum):
    Boolean = 1
    Byte = 2
    Char = 3
    Decimal = 5
    Double = 6
    Int16 = 7
    Int32 = 8
    Int64 = 9
    SByte = 10
    Single = 11
    TimeSpan = 12
    DateTime = 13
    UInt16 = 14
    UInt32 = 15
    UInt64 = 16
    Null = 17
    String = 18


class ClassInfo:
    def __init__(self, stream):
        self.ObjectId = _read_int32(stream)
        self.Name = _read_lpstr(stream)
        self.MemberCount = _read_int32(stream)
        self.MemberNames = []

        for _ in range(self.MemberCount):
            self.MemberNames.append(_read_lpstr(stream))

    def __str__(self):
        return f"<ClassInfo: ObjectId={self.ObjectId}, Name='{self.Name}', " \
               f"MemberCount={self.MemberCount}, MemberNames={self.MemberNames}>"


class ClassTypeInfo:
    def __init__(self, stream):
        self.TypeName = _read_lpstr(stream)
        self.LibraryId = _read_int32(stream)

    def __str__(self):
        return f"<ClassTypeInfo: TypeName={self.TypeName}, LibraryId={self.LibraryId}>"


class MemberTypeInfo:
    def __init__(self, stream, count):
        self.BinaryTypeEnums = []

        for _ in range(count):
            self.BinaryTypeEnums.append(BinaryTypeEnumeration(_read_enum(stream)))

        self.AdditionalInfos = []

        for t in self.BinaryTypeEnums:
            if not t.has_additional_info():
                continue

            if t == BinaryTypeEnumeration.Primitive or t == BinaryTypeEnumeration.PrimitiveArray:
                self.AdditionalInfos.append(PrimitiveTypeEnumeration(_read_enum(stream)))
                continue

            if t == BinaryTypeEnumeration.SystemClass:
                raise NotImplementedError("SystemClass in MemberTypeInfo not supported (yet)")

            if t == BinaryTypeEnumeration.Class:
                self.AdditionalInfos.append(ClassTypeInfo(stream))
                continue

            raise NotImplementedError(f"Unknown BinaryTypeEnum with additional info: {t}")

    def __str__(self):
        return f"<MemberTypeInfo: BinaryTypeEnums={self.BinaryTypeEnums}, AdditionalInfos={self.AdditionalInfos}>"


class Record:
    def __init__(self, stream, record_type=None):
        if record_type:
            self.RecordTypeEnum = record_type
        else:
            self.RecordTypeEnum = RecordTypeEnumeration(_read_enum(stream))

        if self.RecordTypeEnum != self._expected_type_enum():
            raise ParseException(f"{self.RecordTypeEnum} did not match"
                                 f"the expected value of {self._expected_type_enum()}")

    def _expected_type_enum(self):
        raise NotImplementedError("_expected_type_enum is not implemented!")

    def __str__(self):
        return f"<Record: RecordTypeEnum={self.RecordTypeEnum}>"

    @staticmethod
    def from_stream(stream):
        record_type = RecordTypeEnumeration(_read_enum(stream))

        if record_type == RecordTypeEnumeration.SerializedStreamHeader:
            return SerializationHeaderRecord(stream, record_type=record_type)

        if record_type == RecordTypeEnumeration.ClassWithId:
            return ClassWithId(stream, record_type=record_type)

        if record_type == RecordTypeEnumeration.ClassWithMembersAndTypes:
            return ClassWithMembersAndTypes(stream, record_type=record_type)

        if record_type == RecordTypeEnumeration.MessageEnd:
            return MessageEnd(stream, record_type=record_type)

        if record_type == RecordTypeEnumeration.BinaryLibrary:
            return BinaryLibrary(stream, record_type=record_type)

        raise ParseException(f"Unknown record type: {record_type}")


class BinaryObjectString(Record):
    def __init__(self, stream, **kwargs):
        super().__init__(stream, **kwargs)
        self.ObjectId = _read_int32(stream)
        self.Value = _read_lpstr(stream)

    def _expected_type_enum(self):
        return RecordTypeEnumeration.BinaryObjectString

    def __str__(self):
        return f"<BinaryObjectString: ObjectId={self.ObjectId}, Value='{self.Value}'>"


class SerializationHeaderRecord(Record):
    def __init__(self, stream, **kwargs):
        super().__init__(stream, **kwargs)
        self.RootId = _read_int32(stream)
        self.HeaderId = _read_int32(stream)
        self.MajorVersion = _read_int32(stream)
        self.MinorVersion = _read_int32(stream)

    def _expected_type_enum(self):
        return RecordTypeEnumeration.SerializedStreamHeader

    def __str__(self):
        return f"<SerializationHeaderRecord: RootId={self.RootId}, HeaderId={self.HeaderId}, " \
               f"MajorVersion={self.MajorVersion}, MinorVersion={self.MinorVersion}>"


class ClassWithId(Record):
    def __init__(self, stream, **kwargs):
        super().__init__(stream, **kwargs)
        self.ObjectId = _read_int32(stream)
        self.MetadataId = _read_int32(stream)

    def _expected_type_enum(self):
        return RecordTypeEnumeration.ClassWithId

    def __str__(self):
        return f"<ClassWithId: ObjectId={self.ObjectId}, MetadataId={self.MetadataId}>"


class ClassWithMembersAndTypes(Record):
    def __init__(self, stream, **kwargs):
        super().__init__(stream, **kwargs)
        self.ClassInfo = ClassInfo(stream)
        self.MemberTypeInfo = MemberTypeInfo(stream, self.ClassInfo.MemberCount)
        self.LibraryId = _read_int32(stream)

    def _expected_type_enum(self):
        return RecordTypeEnumeration.ClassWithMembersAndTypes

    def __str__(self):
        return f"<ClassWithMembersAndTypes: ClassInfo={self.ClassInfo}, " \
               f"MemberTypeInfo={self.MemberTypeInfo}, LibraryId={self.LibraryId}>"

    def to_object(self, stream, ids):
        cls = type(self.ClassInfo.Name, (), {'__doc__': '.NET class'})

        for attr in self.ClassInfo.MemberNames:
            setattr(cls, attr, None)

        obj = cls()

        add = 0
        for i, t in enumerate(self.MemberTypeInfo.BinaryTypeEnums):
            attr_name = self.ClassInfo.MemberNames[i]

            if t.has_additional_info():
                additional_info = self.MemberTypeInfo.AdditionalInfos[add]
                add += 1

                if t == BinaryTypeEnumeration.Primitive:
                    if additional_info == PrimitiveTypeEnumeration.Int32:
                        setattr(obj, attr_name, _read_int32(stream))
                        continue

                    if additional_info == PrimitiveTypeEnumeration.UInt32:
                        setattr(obj, attr_name, _read_uint32(stream))
                        continue

                    raise NotImplementedError(f"Primitive Type {additional_info}")

            if t == BinaryTypeEnumeration.String:
                record = BinaryObjectString(stream)
                ids[record.ObjectId] = record
                setattr(obj, attr_name, record.Value)
                continue

            raise NotImplementedError(f"Binary Type {t}")

        return obj


class MessageEnd(Record):
    def _expected_type_enum(self):
        return RecordTypeEnumeration.MessageEnd


class BinaryLibrary(Record):
    def __init__(self, stream, **kwargs):
        super().__init__(stream, **kwargs)
        self.LibraryId = _read_int32(stream)
        self.LibraryName = _read_lpstr(stream)

    def _expected_type_enum(self):
        return RecordTypeEnumeration.BinaryLibrary

    def __str__(self):
        return f"<BinaryLibrary: LibraryId={self.LibraryId}, LibraryName='{self.LibraryName}'>"


class SerializedMessage:
    def __init__(self, stream):
        self.header = SerializationHeaderRecord(stream)

        # TODO: The assumption is that the actual data will start once all the
        # required metadata (RootId and its dependencies) has been loaded.
        _required_ids = [self.header.RootId]

        # Quick access map of all the known IDs
        # TODO: Check if there can be overlap between library and object IDs
        self._ids = {}

        self.records = []

        while len(_required_ids) != 0:
            record = Record.from_stream(stream)
            self.records.append(record)

            if isinstance(record, BinaryLibrary):
                if record.LibraryId in self._ids:
                    raise Exception(f"LibraryId {record.LibraryId} is already registered!")

                self._ids[record.LibraryId] = record

            if isinstance(record, ClassWithMembersAndTypes):
                if record.ClassInfo.ObjectId in self._ids:
                    raise Exception(f"ObjectId {record.ClassInfo.ObjectId} is already registered!")

                self._ids[record.ClassInfo.ObjectId] = record

            # Remove all now known IDs from the list of required IDs
            _required_ids = [x for x in _required_ids if x not in self._ids]

        self.object = self._ids[self.header.RootId].to_object(stream, self._ids)
