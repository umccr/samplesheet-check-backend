# Add umccr_util directory to python path
import os
import sys
PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(
    PROJECT_PATH,"..","layers" 
)
sys.path.append(SOURCE_PATH)

