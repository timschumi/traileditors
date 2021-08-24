from enum import Enum

__all__ = [
    'ProtoType',
]


class ProtoType(Enum):
    InputSeatBlockSetup = 0
    SliderBlockSetup = 1
    ToneBlockSetup = 2
    VisitedStateMap = 3
    Vector3 = 4
    Quaternion = 5
    Bounds = 6
    Rect = 7
    StructureGraphSaveDataProto = 8
    BlockBehaviourSetup = 9
    GhostData = 10
    WeldingDataProto = 11
    ListInt = 12
    TrailmakersPlayerSaveData = 13
    StructureSaveIdentifierProto = 14
    StructureMetaDataProto = 15
    TransformationLinksProto = 16
    StructureNodeSaveData = 17
    GameVersion = 18
    SocketLinkHandleDescription = 19
    SerializableColor = 20
    KeyCode = 21
    EAction = 22
    BlockSkinType = 23
    CustomAxisSetup = 24
    SerializableVector3 = 25
    KeyValuePairIntListInt = 26
    BlockUnlockingSystemSaveData = 27
    GoldPlayerSystemSaveData = 28
    BuildPowerSystemSaveData = 29
    CheckpointSystemSaveData = 30
    ShroudSystemSaveData = 31
    UnlockingPlayerSystemSaveData = 32
    SecretSystemSaveData = 33
    StatisticsPlayerSystemSaveData = 34
    TreasureHuntSystemSaveData = 35
    NuggetHuntSystemSaveData = 36
    SalvagePlayerSystemSaveData = 37
    EIdentifierType = 38
    ABuildGridPosition = 39
    ABuildGridRotation = 40
    CellMap = 41
    SimpleBitArray = 42
