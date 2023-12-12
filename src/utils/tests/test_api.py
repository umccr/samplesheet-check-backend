import os
import asyncio
import logging
from unittest import TestCase, mock, main
from utils.api import get_metadata_record_from_array_of_field_name

VALID_GET_RESPONSE = {
    "links": {
        "next": None,
    },
    "results": [
        {
            "id": 2420,
            "library_id": "L2100999",
            "sample_id": "MDX210239",
        }
    ]
}

INVALID_GET_RESPONSE = {
    "links": {
        "next": None,
    },
    "results": []
}


class MockAiohttpResponse:
    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self

    def __init__(self, json_data, status):
        self.json_data = json_data
        self.status = status

    async def json(self):
        return self.json_data


def mock_valid_get_request(*args, **kwargs):
    return MockAiohttpResponse(VALID_GET_RESPONSE, 200)


def mock_invalid_get_request(*args, **kwargs):
    return MockAiohttpResponse(INVALID_GET_RESPONSE, 200)


class ApiUnitTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        logging.disable(logging.CRITICAL)
        print("\n---Running utils api unit tests---")

    @mock.patch('aiohttp.ClientSession.get', side_effect=mock_valid_get_request)
    def test_valid_metadata(self, get_mock):
        valid_parameter = [
            "L2100956",
            "L2100928",
            "L2100934"
        ]

        func_test_result = asyncio.run(get_metadata_record_from_array_of_field_name(path='metadata',
                                                                                    field_name='library_id',
                                                                                    value_list=valid_parameter,
                                                                                    auth_header=os.getenv(
                                                                                        'dev_data_portal_jwt')))

        assert type(func_test_result) is list, "Expected to have a list type data"
        assert len(func_test_result) >= 1, "Expected to have at least a matching data"

    @mock.patch('aiohttp.ClientSession.get', side_effect=mock_invalid_get_request)
    def test_get_invalid_metadata(self, get_mock):
        invalid_parameter = [
            "L-!#$#%^",
            "L-999999",
            "L-ABCDEF"
        ]

        func_test_result = asyncio.run(get_metadata_record_from_array_of_field_name(path='metadata',
                                                                                    field_name='library_id',
                                                                                    value_list=invalid_parameter,
                                                                                    auth_header=os.getenv(
                                                                                        'dev_data_portal_jwt')))

        assert type(func_test_result) is list, "Expected to have a list type data"
        assert len(func_test_result) == 0, "Expected to have at least a matching data"

    def test_invalid_jwt(self):
        invalid_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNvbWVraWQxIn0" \
                      ".eyJpc3MiOiJodHRwczovL2lzczEudW1jY3Iub3JnIiwic3ViIjoiMTIzNDU2Nzg5MCIsIm5hbWUiOiJKb2huIERvZSIsI" \
                      "mlhdCI6MTUxNjIzOTAyMiwiZXhwIjoxNTE2MjM5MDIyLCJnYTRnaF92aXNhX3YxIjp7InR5cGUiOiJDb250cm9sbGVkQWN" \
                      "jZXNzR3JhbnRzIiwiYXNzZXJ0ZWQiOjE1NDk2MzI4NzIsInZhbHVlIjoiaHR0cHM6Ly91bWNjci5vcmcvaW52YWxpZC8xI" \
                      "iwic291cmNlIjoiaHR0cHM6Ly9ncmlkLmFjL2luc3RpdHV0ZXMvZ3JpZC4wMDAwLjBhIiwiYnkiOiJkYWMifX0.5DIqppX" \
                      "02Rkw2Ebk4KgvPlbKVBwS1dPiSeLaLLQDjBg "

        with self.assertRaises(ValueError):
            asyncio.run(get_metadata_record_from_array_of_field_name(invalid_jwt, "", "", [""]))


if __name__ == '__main__':
    main()
