
import json
import urllib.parse
import boto3
import re
from gzip import GzipFile
from io import BytesIO

print('Loading function')

s3 = boto3.client('s3')

# NOTE despite the name this does not currently calculate md5sums


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    print("Bucket %s Key %s" % (bucket, key))
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
    tag = re.sub(r'\W', '', response['ETag'])
    print("ETag: " + tag)
    gz_body = BytesIO()
    gz = GzipFile(None, 'wb', 9, gz_body)
    gz.write(response['Body'].read())
    gz.close()
    try:
        put_res = s3.put_object(Bucket=bucket, Key=key+'.gz', Body=gz_body.getvalue())
    except Exception as e:
        print(e)
        print('Error putting gzipped object {} to bucket {}.'.format(key+'.gz', bucket))
        raise e

    return {'md5sum': tag, 'submitted_file_name': key+'.gz'}
