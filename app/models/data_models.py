from enum import Enum


class EDataType(Enum):
    nfs_file = 0
    nfs_file_processed = 1
    nfs_file_download = 2


class EPipeline(Enum):
    dicom_edit = 0
    data_transfer = 1
