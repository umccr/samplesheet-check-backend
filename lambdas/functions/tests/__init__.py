# Add umccr_util directory to python path
import os
import sys

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
SOURCE_PATH = os.path.join(
    DIR_PATH, "..", "..", "layers"
)
sys.path.append(SOURCE_PATH)

os.environ["data_portal_domain_name"] = "api.data.dev.umccr.org"
