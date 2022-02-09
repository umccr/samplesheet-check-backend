import json
import os
from aiohttp import ClientSession
import requests
from typing import List

# Grab api constant from environment variable
DATA_PORTAL_DOMAIN_NAME = os.environ["data_portal_domain_name"]


async def get_metadata_record_from_array_of_field_name(auth_header: str, path: str, field_name: str,
                                                       value_list: List[str]):
    # Define header request
    headers = {
        'Authorization': auth_header
    }

    # Define query string
    query_param_string = f'&{field_name}='.join(value_list)
    query_param_string = f'?{field_name}=' + query_param_string  # Appending name at the beginning

    query_param_string = query_param_string + f'&rowsPerPage=1000'  # Add Rows per page (1000 is the maximum rows)

    url = "https://" + DATA_PORTAL_DOMAIN_NAME + "/" + path.strip('/') + query_param_string

    query_result = []
    print('Start API request')
    async with ClientSession() as session:

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
    print('Finish API request')
    return query_result
