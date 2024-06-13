install:
	@yarn install
	@pip install -r requirements.txt
	@pip install -r src/requirements.txt


build:
	@yarn cdk synth
	@sam build -t ./cdk.out/assembly-SSCheckBackEndCdkPipeline-SampleSheetCheckBackEndStage/SSCheckBackEndCdkPipelineSampleSheetCheckBackEndStageSampleSheetCheckBackEnd*.template.json --no-cached

start: build
	@sam local start-api --env-vars local-start-env-var.json -p 8001 -t ./cdk.out/assembly-SSCheckBackEndCdkPipeline-SampleSheetCheckBackEndStage/SSCheckBackEndCdkPipelineSampleSheetCheckBackEndStageSampleSheetCheckBackEnd*.template.json
