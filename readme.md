# Cloud - COMSE6998 - Cloud Computing and Big Data

## Assignment 2 - Photo Album

1. Launch an OpenSearch instance
    - Create a domain `photos`
        - CONFIGURATIONS: Standard create > Dev/test > Domain without standby > 1-AZ > 2.9 (latest) > t3.small.search > node: 1 > Public access > Dual-stack mode - recommended > Create master user > Do not set domain level access policy > Use AWS owned key

2. Upload and Index Photos
    - Create an S3 bucket   `b2-imgs`
    - Create a Lambda Function (LF1) `index-photos`
    - S3 bucket `b2-imgs` GIVE PERMISSIONS
        - Permissions > Block all public access > Off
    - LF1 `index-photos` PUT EVENT TRIGGER
        - When photo is added to S3 `b2-imgs`, it triggers LF1 `index-photos`
        - CONFIGURATIONS: Add Trigger > S3 > Bucket: b2-imgs > Event Types: All object create events, PUT
    - LF1 function
        - image is added to bucket S3
        - Rekognition detects labels in image
        - S3 SDK’s headObject method > retrieve the S3 metadata created at the object’s upload time > get x-amz-meta-customLabels metadata field if it exists > create json array of all labels from Rekognition and S3 SDK's headobject
        - Save the json in OpenSearch `photos`
            ```js
                {
                    “objectKey”: “my-photo.jpg”,
                    “bucket”: “my-photo-bucket”,
                    “createdTimestamp”: “2018-11-05T12:40:02”,
                    “labels”: [
                        “person”,
                        “dog”,
                        “ball”,
                        “park”
                    ]
                }
            ```
    - Give OpenSearch and Lambda Function permission to use each other
        - In Lambda Function > Configuration > Role name > Copy the Lambda function Role ARN
        - In OpenSearch > domains > index_name > Security configuration > Edit > Set IAM ARN as master user > Paste the Lambda function Role ARN > Only use fine-grained access control > Save changes
    - NOTE: LF1 function will be imported as a zip file -> for ease you can import the zip file ["deployment.zip"](./deployment.zip)

3. Search
    - Create a Lambda Function (LF2) `search-photos`
    - Create Lex Bot `search-bot`
        - CONFIGURATIONS: name: search-bot > IAMPermissions: Create a role with basic Amazon Lex permissions > COPPA: No > Done
    - Create a new Intent 
        - name: SearchIntent1Key
        - description: extract one key from the user
        - Add a slot => name: `key1`; type: `alphanumeric`; prompt: `Enter a key`
        - Add sample utterances => `show me {key1}` ... `show me photos with {key1} in them` ... `I would like to see some {key1} photos` ... `could you show me photos of {key1}`
    - Create another Intent for two keys
        - name: SearchIntent2Key
        - description: extract two keys from the user
        - Add a slot => name: `key1`; type: `alphanumeric`; prompt: `Enter a key1`
        - Add a slot => name: `key2`; type: `alphanumeric`; prompt: `Enter a key2`
        - Add sample utterances => `show me {key1} and {key2}` ... `show me photos with {key1} and {key2} in them` ... `I would like to see some {key1} and {key2} photos` ... `could you show me photos of {key1} and {key2}`
    - Implement LF2 function
        - STEP 1: GIVEN QUERY BY USER
        - STEP 2: REMOVE AMBIGUITY SUCH THAT OUR LEX RETURNS KEYWORDS
        - STEP 3: SEARCH OPENSEARCH FOR KEYWORDS AND RETURN PICTURES
    - Give OpenSearch and Lambda Function permission to use each other
        - In Lambda Function > Configuration > Role name > Copy the Lambda function Role ARN
        - In OpenSearch > domains > index_name > Security configuration > Edit > Set IAM ARN as master user > Paste the Lambda function Role ARN > Only use fine-grained access control > Save changes

4. API GateWay
    - Create REST API > REST > Import from Swagger or Open API 3 > Paste your [Swagger Code](./swagger.yaml)
    - Create a new role that allows API Gateway to push logs to Cloudwatch Logs
        - Identity and Access Management (IAM) > Roles > Create Role > AWS Service > API Gateway (Allows API Gateway to push logs to CloudWatch Logs) > Give role name
        - Copy the ARN of the Role
    - PUT: add image to S3
        - API Gateway > APIs > Resources - AI Photo Search > Click on PUT (/upload/{bucket}/{filename} - PUT - Method execution) > Edit Integration > AWS service > AWS Region: us-east-1 > AWS service: S3 > AWS subdomain: null > HTTP method: PUT > Use path override: upload/{bucket}/{filename} > Execution role: PASTE YOUR ARN ROLE HERE > URL path parameters > `bucket:method.request.path.bucket; filename:method.request.path.filename`
    - GET: extract data from opensearch and display
        - API Gateway > APIs > Resources - AI Photo Search > Click on GET > Edit Integration > Lambda function > `search-photos` > Lambda proxy integration: enable this > URL query string parameters: `q:method.request.querystring.q`
    - Deployment
        - Deploy API > Select new stage > Name the new stage > Deploy
        - Stages > (Name of the stage) > Stage actions > Generate SDK > Platform: JavaScript
        - Copy paste the [apigClient.js](./frontend/apigClient.js) and [lib/](./frontend/lib/) in your [frontend directory](./frontend/)


5. Frontend
    - Write a frontend code to
        - [Index.html](./frontend/index.html): the main landing page
        - [Gallery.html](./frontend/gallery.html): This is to search in the gallery for our keywords
        - [Upload.html](./frontend/upload.html): This is to upload image to gallery
    - Deploy FE in S3 bucket
        - CONFIGURATIONS: type bucket name (photo-gallery-fe) > Block all public access > Create
        - Go to your S3 bucket you just created > Upload files
        - Permissions > Bucket policy > Write bucket policy as below
            ```json
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "PublicReadGetObject",
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": "arn:aws:s3:::photo-gallery-fe/*"
                    }
                ]
            }
            ```




- curl -i --location --request PUT 'https://a3bkr5s9v9.execute-api.us-east-1.amazonaws.com/gbm2/upload/b2-imgs/tree3.jpeg' --header 'Content-Type: image/jpeg' --data-binary '/Users/tanishabisht/Desktop/tree3.jpeg'