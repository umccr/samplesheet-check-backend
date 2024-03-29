import json
import os
import aiohttp
import requests
from typing import List
from urllib.parse import urlparse

# Grab api constant from environment variable
DATA_PORTAL_DOMAIN_NAME = os.environ["data_portal_domain_name"]


async def get_metadata_record_from_array_of_field_name(auth_header: str, path: str, field_name: str,
                                                       value_list: List[str]):
    # Define header request
    headers = {
        'Authorization': auth_header
    }

    # Removing any duplicates for api efficiency
    value_list = list(set(value_list))

    # Result variable
    query_result = []

    async with aiohttp.ClientSession() as session:

        # Set maximum batch API call to 300 to prevent "Request Header Fields Too Large"
        max_number_of_library_per_api_call = 300
        for i in range(0, len(value_list), max_number_of_library_per_api_call):

            # Define start and stop element from the list
            start_index = i
            end_index = start_index + max_number_of_library_per_api_call

            array_to_process = value_list[start_index:end_index]

            # Define query string
            query_param_string = f'&{field_name}='.join(array_to_process)
            query_param_string = f'?{field_name}=' + query_param_string  # Appending name at the beginning

            query_param_string = query_param_string + f'&rowsPerPage=1000'  # Add Rows per page (1000 is the maximum rows)

            if not urlparse(DATA_PORTAL_DOMAIN_NAME).scheme == "":
                url = DATA_PORTAL_DOMAIN_NAME + "/" + path.strip('/') + query_param_string
            else:
                url = "https://" + DATA_PORTAL_DOMAIN_NAME + "/" + path.strip('/') + query_param_string

            # Make sure no data is left, looping data until the end
            while url is not None:

                async with session.get(url, headers=headers) as response:

                    # API call
                    response_json = await response.json()

                    # Raise an error for non 200 status code
                    if response.status < 200 or response.status >= 300:
                        raise ValueError(f'Non 20X status code returned')

                    query_result.extend(response_json["results"])
                    url = response_json["links"]["next"]

    return query_result
