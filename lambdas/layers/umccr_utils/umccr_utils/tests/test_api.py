# Add umccr_util directory to python path
import os, json

from unittest import TestCase, mock, main
from umccr_utils.api import get_metadata_record_from_array_of_field_name

"""Mock requests get function"""


def mocked_valid_get_requests(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    expected_result = {
        "results": [
            {
                "id": 2420,
                "library_id": "L2100999",
                "sample_id": "MDX210239",
            }
        ]
    }

    return MockResponse(expected_result, 200)


def mocked_invalid_get_requests(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    expected_result = {
        "results": []
    }
    return MockResponse(expected_result, 200)


class ApiUnitTestCase(TestCase):
    """Start UnitTest"""


    ### Testing valid parameter
    @mock.patch('umccr_utils.api.aiohttp.ClientSession.get', side_effect=mocked_valid_get_requests)
    async def test_valid_metadata(self, mock_get):
        # A list of tuple which contain a valid existing data
        # Format: ( SampleID, LibraryID )
        valid_parameter = [
            "L2100956",
            "L2100928",
            "L2100934"
        ]

        func_test_result = await get_metadata_record_from_array_of_field_name(path='metadata',
                                                                              field_name='library_id',
                                                                              value_list=valid_parameter,
                                                                              auth_header=os.getenv(
                                                                                  'dev_data_portal_jwt'))
        assert type(func_test_result) is list, "Expected to have a list type data"
        assert len(func_test_result) >= 1, "Expected to have at least a matching data"

    @mock.patch('umccr_utils.api.aiohttp.ClientSession.get', side_effect=mocked_invalid_get_requests)
    async def test_get_invalid_metadata(self, get_mock):
        # A list of tuple which contain a valid existing data
        # Format: ( SampleID, LibraryID )
        invalid_parameter = [
            "L-!#$#%^",
            "L-999999",
            "L-ABCDEF"
        ]

        func_test_result = await get_metadata_record_from_array_of_field_name(path='metadata',
                                                                              field_name='library_id',
                                                                              value_list=invalid_parameter,
                                                                              auth_header=os.getenv(
                                                                                  'dev_data_portal_jwt'))

        assert type(func_test_result) is list, "Expected to have a list type data"
        assert len(func_test_result) == 0, "Expected to have at least a matching data"

    ### Test invalid jwt
    async def test_get_invalid_token(self):
        invalid_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNvbWVraWQxIn0.eyJpc3MiOiJodHRwczovL2lzczEudW1jY3Iub3JnIiwic3ViIjoiMTIzNDU2Nzg5MCIsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTUxNjIzOTAyMiwiZXhwIjoxNTE2MjM5MDIyLCJnYTRnaF92aXNhX3YxIjp7InR5cGUiOiJDb250cm9sbGVkQWNjZXNzR3JhbnRzIiwiYXNzZXJ0ZWQiOjE1NDk2MzI4NzIsInZhbHVlIjoiaHR0cHM6Ly91bWNjci5vcmcvaW52YWxpZC8xIiwic291cmNlIjoiaHR0cHM6Ly9ncmlkLmFjL2luc3RpdHV0ZXMvZ3JpZC4wMDAwLjBhIiwiYnkiOiJkYWMifX0.5DIqppX02Rkw2Ebk4KgvPlbKVBwS1dPiSeLaLLQDjBg"

        with self.assertRaises(ValueError):
            await get_metadata_record_from_array_of_field_name(invalid_jwt, "", "", [""], "")


if __name__ == '__main__':
    main()
