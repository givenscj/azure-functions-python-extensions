#  Copyright (c) Microsoft Corporation. All rights reserved.
#  Licensed under the MIT License.

import json
import unittest
from enum import Enum
from typing import Optional

from azure.storage.blob import StorageStreamDownloader as SSDSdk
from azurefunctions.extensions.base import Datum

from azurefunctions.extensions.bindings.blob import (
    BlobClientConverter,
    StorageStreamDownloader,
)


# Mock classes for testing
class MockMBD:
    def __init__(self, version: str, source: str, content_type: str, content: str):
        self.version = version
        self.source = source
        self.content_type = content_type
        self.content = content


class MockBindingDirection(Enum):
    IN = 0
    OUT = 1
    INOUT = 2


class MockBinding:
    def __init__(
        self,
        name: str,
        direction: MockBindingDirection,
        data_type=None,
        type: Optional[str] = None,
    ):  # NoQa
        self.type = type
        self.name = name
        self._direction = direction
        self._data_type = data_type
        self._dict = {
            "direction": self._direction,
            "dataType": self._data_type,
            "type": self.type,
        }

    @property
    def data_type(self) -> Optional[int]:
        return self._data_type.value if self._data_type else None

    @property
    def direction(self) -> int:
        return self._direction.value


class MockParamTypeInfo:
    def __init__(self, binding_name: str, pytype: type):
        self.binding_name = binding_name
        self.pytype = pytype


class MockFunction:
    def __init__(self, bindings: MockBinding):
        self._bindings = bindings


class TestStorageStreamDownloader(unittest.TestCase):
    def test_input_type(self):
        check_input_type = BlobClientConverter.check_input_type_annotation
        self.assertTrue(check_input_type(StorageStreamDownloader))
        self.assertFalse(check_input_type(str))
        self.assertFalse(check_input_type(bytes))
        self.assertFalse(check_input_type(bytearray))

    def test_input_none(self):
        result = BlobClientConverter.decode(
            data=None, trigger_metadata=None, pytype=StorageStreamDownloader
        )
        self.assertIsNone(result)

        datum: Datum = Datum(value=b"string_content", type=None)
        result = BlobClientConverter.decode(
            data=datum, trigger_metadata=None, pytype=StorageStreamDownloader
        )
        self.assertIsNone(result)

    def test_input_incorrect_type(self):
        datum: Datum = Datum(value=b"string_content", type="bytearray")
        with self.assertRaises(ValueError):
            BlobClientConverter.decode(
                data=datum, trigger_metadata=None, pytype=StorageStreamDownloader
            )

    def test_input_empty(self):
        datum: Datum = Datum(value={}, type="model_binding_data")
        result: StorageStreamDownloader = BlobClientConverter.decode(
            data=datum, trigger_metadata=None, pytype=StorageStreamDownloader
        )
        self.assertIsNone(result)

    def test_input_populated(self):
        content = {
            "Connection": "AzureWebJobsStorage",
            "ContainerName": "test-blob",
            "BlobName": "text.txt",
        }

        sample_mbd = MockMBD(
            version="1.0",
            source="AzureStorageBlobs",
            content_type="application/json",
            content=json.dumps(content),
        )

        datum: Datum = Datum(value=sample_mbd, type="model_binding_data")
        result: StorageStreamDownloader = BlobClientConverter.decode(
            data=datum, trigger_metadata=None, pytype=StorageStreamDownloader
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SSDSdk)

        sdk_result = StorageStreamDownloader(data=datum.value).get_sdk_type()

        self.assertIsNotNone(sdk_result)
        self.assertIsInstance(sdk_result, SSDSdk)

    def test_invalid_input_populated(self):
        content = {
            "Connection": "NotARealConnectionString",
            "ContainerName": "test-blob",
            "BlobName": "text.txt",
        }

        sample_mbd = MockMBD(
            version="1.0",
            source="AzureStorageBlobs",
            content_type="application/json",
            content=json.dumps(content),
        )

        with self.assertRaises(ValueError) as e:
            datum: Datum = Datum(value=sample_mbd, type="model_binding_data")
            result: StorageStreamDownloader = BlobClientConverter.decode(
                data=datum, trigger_metadata=None, pytype=StorageStreamDownloader
            )
        self.assertEqual(
            e.exception.args[0],
            "Storage account connection string NotARealConnectionString does not exist. "
            "Please make sure that it is a defined App Setting.",
        )

    def test_none_input_populated(self):
        content = {
            "Connection": None,
            "ContainerName": "test-blob",
            "BlobName": "text.txt",
        }

        sample_mbd = MockMBD(
            version="1.0",
            source="AzureStorageBlobs",
            content_type="application/json",
            content=json.dumps(content),
        )

        with self.assertRaises(ValueError) as e:
            datum: Datum = Datum(value=sample_mbd, type="model_binding_data")
            result: StorageStreamDownloader = BlobClientConverter.decode(
                data=datum, trigger_metadata=None, pytype=StorageStreamDownloader
            )
        self.assertEqual(
            e.exception.args[0],
            "Storage account connection string cannot be None. Please provide a connection string.",
        )

    def test_input_populated_managed_identity_input(self):
        content = {
            "Connection": "input",
            "ContainerName": "test-blob",
            "BlobName": "text.txt",
        }

        sample_mbd = MockMBD(
            version="1.0",
            source="AzureStorageBlobs",
            content_type="application/json",
            content=json.dumps(content),
        )

        datum: Datum = Datum(value=sample_mbd, type="model_binding_data")
        result: StorageStreamDownloader = BlobClientConverter.decode(
            data=datum, trigger_metadata=None, pytype=StorageStreamDownloader
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SSDSdk)

        sdk_result = StorageStreamDownloader(data=datum.value).get_sdk_type()

        self.assertIsNotNone(sdk_result)
        self.assertIsInstance(sdk_result, SSDSdk)

    def test_input_populated_managed_identity_trigger(self):
        content = {
            "Connection": "trigger",
            "ContainerName": "test-blob",
            "BlobName": "text.txt",
        }

        sample_mbd = MockMBD(
            version="1.0",
            source="AzureStorageBlobs",
            content_type="application/json",
            content=json.dumps(content),
        )

        datum: Datum = Datum(value=sample_mbd, type="model_binding_data")
        result: StorageStreamDownloader = BlobClientConverter.decode(
            data=datum, trigger_metadata=None, pytype=StorageStreamDownloader
        )

        self.assertIsNotNone(result)
        self.assertIsInstance(result, SSDSdk)

        sdk_result = StorageStreamDownloader(data=datum.value).get_sdk_type()

        self.assertIsNotNone(sdk_result)
        self.assertIsInstance(sdk_result, SSDSdk)

    def test_input_invalid_pytype(self):
        content = {
            "Connection": "AzureWebJobsStorage",
            "ContainerName": "test-blob",
            "BlobName": "text.txt",
        }

        sample_mbd = MockMBD(
            version="1.0",
            source="AzureStorageBlobs",
            content_type="application/json",
            content=json.dumps(content),
        )

        datum: Datum = Datum(value=sample_mbd, type="model_binding_data")
        result: StorageStreamDownloader = BlobClientConverter.decode(
            data=datum, trigger_metadata=None, pytype="str"
        )

        self.assertIsNone(result)

    def test_ssd_invalid_creation(self):
        # Create test binding
        mock_blob = MockBinding(
            name="blob", direction=MockBindingDirection.IN, data_type=None, type="blob"
        )

        # Create test input_types dict
        mock_input_types = {
            "blob": MockParamTypeInfo(binding_name="blobTrigger", pytype=bytes)
        }

        # Create test indexed_function
        mock_indexed_functions = MockFunction(bindings=[mock_blob])

        dict_repr, logs = BlobClientConverter.get_raw_bindings(
            mock_indexed_functions, mock_input_types
        )

        self.assertEqual(
            dict_repr,
            [
                '{"direction": "MockBindingDirection.IN", '
                '"type": "blob", '
                '"properties": '
                '{"SupportsDeferredBinding": false}}'
            ],
        )

        self.assertEqual(logs, {"blob": {bytes: "False"}})

    def test_ssd_valid_creation(self):
        # Create test binding
        mock_blob = MockBinding(
            name="client",
            direction=MockBindingDirection.IN,
            data_type=None,
            type="blob",
        )

        # Create test input_types dict
        mock_input_types = {
            "client": MockParamTypeInfo(
                binding_name="blobTrigger", pytype=StorageStreamDownloader
            )
        }

        # Create test indexed_function
        mock_indexed_functions = MockFunction(bindings=[mock_blob])

        dict_repr, logs = BlobClientConverter.get_raw_bindings(
            mock_indexed_functions, mock_input_types
        )

        self.assertEqual(
            dict_repr,
            [
                '{"direction": "MockBindingDirection.IN", '
                '"type": "blob", '
                '"properties": '
                '{"SupportsDeferredBinding": true}}'
            ],
        )

        self.assertEqual(logs, {"client": {StorageStreamDownloader: "True"}})
