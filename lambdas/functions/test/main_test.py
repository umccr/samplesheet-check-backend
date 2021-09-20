# Add umccr_util directory to python path
import sys, os
sys.path.append(os.path.join(sys.path[0],'..'))
sys.path.append(os.path.join(sys.path[0],'..','..'))
sys.path.append(os.path.join(sys.path[0],'..','..', 'layers'))

import json
import sys
from functions.main import lambda_handler

# Declaring truncated test data input
test_data_1 = r"""
{
	"resource": "/",
	"path": "/",
	"httpMethod": "POST",
	"headers": {
		"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNvbWVraWQxIn0.eyJpc3MiOiJodHRwczovL2lzczEudW1jY3Iub3JnIiwic3ViIjoiMTIzNDU2Nzg5MCIsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTUxNjIzOTAyMiwiZXhwIjoxNTE2MjM5MDIyLCJnYTRnaF92aXNhX3YxIjp7InR5cGUiOiJDb250cm9sbGVkQWNjZXNzR3JhbnRzIiwiYXNzZXJ0ZWQiOjE1NDk2MzI4NzIsInZhbHVlIjoiaHR0cHM6Ly91bWNjci5vcmcvaW52YWxpZC8xIiwic291cmNlIjoiaHR0cHM6Ly9ncmlkLmFjL2luc3RpdHV0ZXMvZ3JpZC4wMDAwLjBhIiwiYnkiOiJkYWMifX0.5DIqppX02Rkw2Ebk4KgvPlbKVBwS1dPiSeLaLLQDjBg",
		"Content-Type": "multipart/form-data; boundary=--------------------------209002070246880516195198"
	},
	"body": "----------------------------209002070246880516195198\r\nContent-Disposition: form-data; name=\"logLevel\"\r\n\r\nERROR\r\n----------------------------209002070246880516195198\r\nContent-Disposition: form-data; name=\"file\"; filename=\"sample-1\"\r\nContent-Type: application/octet-stream\r\n\r\n[Header],,,,,,,,,,\nIEMFileVersion,5,,,,,,,,,\nExperiment Name,Tsqn210615-210629_1Jul21,,,,,,,,,\nDate,1/07/2021,,,,,,,,,\nWorkflow,GenerateFASTQ,,,,,,,,,\nApplication,NovaSeq FASTQ Only,,,,,,,,,\nInstrument Type,NovaSeq,,,,,,,,,\nAssay,TruSeq Nano DNA,,,,,,,,,\nIndex Adapters,IDT-ILMN TruSeq DNA UD Indexes (96 Indexes),,,,,,,,,\nChemistry,Amplicon,,,,,,,,,\n,,,,,,,,,,\n[Reads],,,,,,,,,,\n151,,,,,,,,,,\n151,,,,,,,,,,\n,,,,,,,,,,\n[Settings],,,,,,,,,,\nAdapter,AGATCGGAAGAGCACACGTCTGAACTCCAGTCA,,,,,,,,,\nAdapterRead2,AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT,,,,,,,,,\n,,,,,,,,,,\n[Data],,,,,,,,,,\r\n----------------------------209002070246880516195198--\r\n",
	"isBase64Encoded": "false"
}
"""

expected_result_1 = r"""
{
  "checkStatus": "PASS",
  "errorMessage": "",
  "log_file": ""
}
"""

test_data_2 =r"""
{
    "resource": "/",
    "path": "/",
    "httpMethod": "POST",
    "headers": {
      "Accept": "*/*",
      "Accept-Encoding": "gzip, deflate, br",
      "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InNvbWVraWQxIn0.eyJpc3MiOiJodHRwczovL2lzczEudW1jY3Iub3JnIiwic3ViIjoiMTIzNDU2Nzg5MCIsIm5hbWUiOiJKb2huIERvZSIsImlhdCI6MTUxNjIzOTAyMiwiZXhwIjoxNTE2MjM5MDIyLCJnYTRnaF92aXNhX3YxIjp7InR5cGUiOiJDb250cm9sbGVkQWNjZXNzR3JhbnRzIiwiYXNzZXJ0ZWQiOjE1NDk2MzI4NzIsInZhbHVlIjoiaHR0cHM6Ly91bWNjci5vcmcvaW52YWxpZC8xIiwic291cmNlIjoiaHR0cHM6Ly9ncmlkLmFjL2luc3RpdHV0ZXMvZ3JpZC4wMDAwLjBhIiwiYnkiOiJkYWMifX0.5DIqppX02Rkw2Ebk4KgvPlbKVBwS1dPiSeLaLLQDjBg",
      "Content-Type": "multipart/form-data; boundary=--------------------------909838994200765134534563"
    },
    "body": "----------------------------909838994200765134534563\r\nContent-Disposition: form-data; name=\"logLevel\"\r\n\r\nERROR\r\n----------------------------909838994200765134534563\r\nContent-Disposition: form-data; name=\"file\"; filename=\"sample-2\"\r\nContent-Type: application/octet-stream\r\n\r\n[Header],,,,,,,,,,,\nIEMFileVersion,5,,,,,,,,,,\nExperiment Name,TSOR190808-Tsqn190814-STR190829-TSqN190930-STTM20_02Oct19,,,,,,,,,,\nDate,1/10/2019,,,,,,,,,,\nWorkflow,GenerateFASTQ,,,,,,,,,,\nApplication,NovaSeq FASTQ Only,,,,,,,,,,\nInstrument Type,NovaSeq,,,,,,,,,,\nAssay,TruSeq Nano DNA,,,,,,,,,,\nIndex Adapters,IDT-ILMN TruSeq DNA UD Indexes (96 Indexes),,,,,,,,,,\nDescription,,,,,,,,,,,\nChemistry,Amplicon,,,,,,,,,,\n,,,,,,,,,,,\n[Reads],,,,,,,,,,,\n151,,,,,,,,,,,\n151,,,,,,,,,,,\n,,,,,,,,,,,\n[Settings],,,,,,,,,,,\nAdapter,AGATCGGAAGAGCACACGTCTGAACTCCAGTCA,,,,,,,,,,\nAdapterRead2,AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT,,,,,,,,,,\n,,,,,,,,,,,\n[Data],,,,,,,,,,,\n\r\n----------------------------909838994200765134534563--\r\n",
    "isBase64Encoded": "false"
}
"""
expected_result_2 = r"""
{
  "checkStatus": "FAIL",
  "errorMessage": "Found at least two indexes that were too similar to each other",
  "log_file": "2021-09-07 07:37:58,187 - ERROR    - samplesheet               - check_sample_sheet_for_index_clashes     : LineNo. 610  - i7 indexes ATTCAGAA and GTTGAGAA are too similar to run in the same lanewith i5 indexes AGGCTATA and  are too similar to run in the same lane \n2021-09-07 07:37:58,827 - ERROR    - samplesheet               - check_sample_sheet_for_index_clashes     : LineNo. 610  - i7 indexes TGGATCGA and TGGATTGC are too similar to run in the same lanewith i5 indexes GTGCGATA and  are too similar to run in the same lane \n2021-09-07 07:37:58,865 - ERROR    - samplesheet               - check_sample_sheet_for_index_clashes     : LineNo. 610  - i7 indexes TGGATCGA and GTGATCGA are too similar to run in the same lanewith i5 indexes GTGCGATA and  are too similar to run in the same lane \n2021-09-07 07:37:59,425 - ERROR    - samplesheet_check          - run_check                                : LineNo. 167  - Found at least two indexes that were too similar to each other\n"
}
"""
def test_lambda_handler_PASS(mocker):
  # Patch function to return no error
  mocker.patch('functions.main.SampleSheet', return_value="")
  mocker.patch('functions.main.run_check', return_value="")

  # Parse input to JSON
  json_input = json.loads(test_data_1)
  json_expected_result = json.loads(expected_result_1)

  # Create an empty log file
  open('/tmp/samplesheet_check.log', "x")

  # Run the function
  body_result = json.loads(lambda_handler(json_input, ""))["body"]
  
  assert json.loads(body_result) == json_expected_result, "Unexpected Value"


def test_lambda_handler_FAIL(mocker):
  # Patch function to return no error
  mocker.patch('functions.main.SampleSheet', return_value="")
  mocker.patch('functions.main.run_check', return_value="Found at least two indexes that were too similar to each other")

  # Parse input to JSON
  json_input = json.loads(test_data_2)
  json_expected_result = json.loads(expected_result_2)

  # Create log file with error content
  f = open('/tmp/samplesheet_check.log', "a")
  f.write("2021-09-07 07:37:58,187 - ERROR    - samplesheet               - check_sample_sheet_for_index_clashes     : LineNo. 610  - i7 indexes ATTCAGAA and GTTGAGAA are too similar to run in the same lanewith i5 indexes AGGCTATA and  are too similar to run in the same lane \n2021-09-07 07:37:58,827 - ERROR    - samplesheet               - check_sample_sheet_for_index_clashes     : LineNo. 610  - i7 indexes TGGATCGA and TGGATTGC are too similar to run in the same lanewith i5 indexes GTGCGATA and  are too similar to run in the same lane \n2021-09-07 07:37:58,865 - ERROR    - samplesheet               - check_sample_sheet_for_index_clashes     : LineNo. 610  - i7 indexes TGGATCGA and GTGATCGA are too similar to run in the same lanewith i5 indexes GTGCGATA and  are too similar to run in the same lane \n2021-09-07 07:37:59,425 - ERROR    - samplesheet_check          - run_check                                : LineNo. 167  - Found at least two indexes that were too similar to each other\n")
  f.close()

  # Run the function
  body_result = json.loads(lambda_handler(json_input, ""))["body"]

  # Assert to check expected result
  assert json.loads(body_result) == json_expected_result, "Unexpected Value"
