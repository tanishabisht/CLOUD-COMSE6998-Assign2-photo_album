import json
import boto3
import time
import requests
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


# CONSTANTS
OPENSEARCH_ENDPOINT = "https://search-photos-lwaf6zvsq74hrr6gmapeqmbnzm.us-east-1.es.amazonaws.com/photos/"
REGION = 'us-east-1'
HOST = 'search-photos-lwaf6zvsq74hrr6gmapeqmbnzm.us-east-1.es.amazonaws.com'
INDEX = 'photos'

# GET OPENSEARCH AUTHENTICATION
def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
        cred.secret_key,
        region,
        service,
        session_token=cred.token
    )

# DEFINING CLIENTS
lex_client = boto3.client('lexv2-runtime', region_name=REGION)
os_client = OpenSearch(
    hosts=[{ 'host': HOST, 'port': 443 }],
    http_auth=get_awsauth(REGION, 'es'),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

def response_from_lex(text_from_user):
    # get response from lex
    response = lex_client.recognize_text(
        botId='YKAI3LZNLQ',
        botAliasId='TSTALIASID',
        localeId='en_US',
        sessionId='testuser',
        text=text_from_user
    )
    print("lex response --- ", response)
    
    # get slots
    slots = response.get('sessionState', {}).get('intent', {}).get('slots', {})
    print("lex slots --- ", slots)

    # extract keys from slots
    keys_arr = []
    for key, value in slots.items():
        if key == 'key1':
            keys_arr.append(value['value']['interpretedValue'])
        if key == 'key2':
            keys_arr.append(value['value']['interpretedValue'])
    
    print("lex keys --- ", keys_arr)
    return keys_arr
    


def response_from_opensearch(key):
    try:
        q = { 'size': 5, "query": { "bool": { "should": [{"match": {"labels": key}}]}}}
        response = os_client.search(index=INDEX, body=q)
        print("os response: ", response)
        images_from_key = []
        for hit in response['hits']['hits']:
            images_from_key.append(hit['_source'])
        print("os result: ", images_from_key)
        return images_from_key
    except Exception as e:
        print(f"Error searching OpenSearch index: {e}")
        return []
    


def lambda_handler(event, context):
    print("event: ", event)
    print("context: ", context)
    
    # STEP 1: GIVEN QUERY BY USER
    text_from_user = event['user']
    
    # STEP 2: REMOVE AMBIGUITY SUCH THAT OUR LEX RETURNS KEYWORDS
    keys = response_from_lex(text_from_user)
    
    # STEP 3: SEARCH OPENSEARCH FOR KEYWORDS AND RETURN PICTURES
    finalImages = []
    for key in keys:
        print("key: ", key)
        images_from_key = response_from_opensearch(key)
        finalImages.append(images_from_key)

    return {
        'statusCode': 200,
        'event': event,
        'keys': keys,
        'finalImages': finalImages
    }