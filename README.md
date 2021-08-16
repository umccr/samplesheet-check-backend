
# samplesheet-check-backend

Project is the samplesheet check for the UMCCR bakcend infrastructure.

The project contains the `app.py` that is the main function of the app and directories:

- *lambdas* -  the lambdas source code lives
  - *functions* - the logic for the main function
  - *layers* - dependencies for the function code to run
- *stacks* - the stack for which the code is structured at AWS

## To deploy the project

Before deploy the project layers **must** be compiled and zipped with the following command.

### Lambda layer requirement
This stack deploys Lambda layers to provide runtime code to the Lambda function. Consequently, the Lambda layers must be built prior to stack deployment. This is done by running `build_lambda_layers.sh` on each Lambda layer directory in `lambda/layers/`. Run the following command to meet the lambda layer requirements. [Docker is required]

```bash
for dir in $(find ./lambdas/layers/ -maxdepth 1 -mindepth 1 -type d); do
  ./build_lambda_layers.sh ${dir};
done
```
### Deploying the cdk

After successfully build, you can deploy the cdk with the following command

`cdk deploy`


# cdk Information
The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

