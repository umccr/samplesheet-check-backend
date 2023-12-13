FROM public.ecr.aws/lambda/python:3.11-arm64

WORKDIR ${LAMBDA_TASK_ROOT}
COPY ./src ./

# Install the specified packages
RUN pip install -r requirements.txt

# Specify entrypoint
CMD [ "handler.lambda_handler" ]
