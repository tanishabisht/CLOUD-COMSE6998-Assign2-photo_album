import json
import boto3
import time
import requests

OPENSEARCH_ENDPOINT = "https://search-photos-lwaf6zvsq74hrr6gmapeqmbnzm.us-east-1.es.amazonaws.com/photos/"

def lambda_handler(event, context):
    print("event: ", event)
    print("context: ", context)
    
    s3_bucket = event["Records"][0]["s3"]["bucket"]["name"]
    s3_img = event["Records"][0]["s3"]["object"]["key"]
    
    open_search_url = OPENSEARCH_ENDPOINT + s3_img
    
    # === REKOGNITION ===
    reko = boto3.client('rekognition')
    s3_client = boto3.client('s3')
    reko_labels = reko.detect_labels(Image={'S3Object':{'Bucket':s3_bucket,'Name':s3_img}})
    print("reko_labels: ", reko_labels)
    
    # === S3 -> X-AMZ ===
    s3_res = s3_client.head_object(Bucket=s3_bucket, Key=s3_img)
    print("s3_res: ", s3_res)
    if 'x-amz-meta-customLabels' in s3_res['Metadata']:
        custom_labels_metadata = response['Metadata']['x-amz-meta-customLabels']
        custom_labels_json = json.loads(custom_labels_metadata)
        print("x-amz-meta-customLabels: ", custom_labels_json)
    else:
        print("x-amz-meta-customLabels metadata field not found.")
    
    # === ADD OBJECT TO OPENSEARCH ===
    try:
        data = {}
        data["objectKey"] = s3_img
        data["bucket"] = s3_bucket
        data["createdTimestamp"] = time.time()
        data['labels'] = []
        for label in reko_labels['Labels']:
            data['labels'].append(label['Name'])
        json_data = json.dumps(data)
        headers = { "Content-Type": "application/json" }
        r = requests.post(url = open_search_url, data = json_data, headers = headers)
        print("opensource request: ", r)
    except Exception as e:
        print("Error: "+ str(e))
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from LF1 Function! The task is to index the photos from S3 bucket in OpenSearch')
    }

