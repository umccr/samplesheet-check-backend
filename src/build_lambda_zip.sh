# Install and zipped dependencies
mkdir -p package
pip install --target ./package -r requirements.txt
cd package
zip -r ../dependencies.zip .
cd ..

zip -r ../deployment_lambda.zip .
