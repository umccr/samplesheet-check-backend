import requests
import os

from typing import List

# Grab api constant from environment variable
DATA_PORTAL_DOMAIN_NAME = os.environ["data_portal_domain_name"]


def get_metadata_record_from_array_of_field_name(auth_header: str, path: str, field_name: str, value_list: List[str]):

    # Define heaeder request
    headers = {
        'Authorization': auth_header
    }

    # Define query string
    query_param_string = f'&{field_name}='.join(value_list)
    query_param_string = f'?{field_name}=' + query_param_string  # Appending name at the beginning

    query_param_string = query_param_string + f'&rowsPerPage=1000'  # Add Rows per page (1000 is the maximum rows)

    url = "https://" + DATA_PORTAL_DOMAIN_NAME + "/" + path + query_param_string

    query_result = []

    # Make sure no data is left, looping data until the end
    while url is not None:

        # API call
        response = requests.get(url, headers=headers)
        response_json = response.json()

        # Raise an error for non 200 status code
        if response.status_code < 200 or response.status_code >= 300:
            print(data)
            raise ValueError

        query_result.extend(response_json["results"])
        url = response_json["links"]["next"]

    return query_result
