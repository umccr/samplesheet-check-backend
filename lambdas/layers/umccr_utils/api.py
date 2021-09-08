import requests
import os

def get_metadata(sample_id_var, library_id_var, auth_header):

  query_str_api = "{} {}".format(sample_id_var, library_id_var)

  # Define API constants
  headers = {
    'Authorization' : auth_header
  }
  parameter = {
    'search' : query_str_api
  }

  # Grab api constant from environment variable
  data_portal_metadata_api = os.environ["data_portal_metadata_api"]

  # API call
  response = requests.get(data_portal_metadata_api,
    params=parameter,
    headers=headers
  )
  
  # Raise an error for non 200 status code
  if response.status_code < 200 or response.status_code >= 300:
    raise ValueError

  data = response.json()

  query_result = data["results"]

  return query_result