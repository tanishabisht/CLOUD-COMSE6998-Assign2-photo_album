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
            ```json
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

