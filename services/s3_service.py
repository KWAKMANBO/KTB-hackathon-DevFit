import boto3
from botocore.config import Config
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
    config=Config(signature_version='s3v4')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME')


def generated_presigned_url(result_key: str, filename: str, content_type: str, expires_in=3600) -> dict:
    # 고유한 파일 키 생성
    ext = filename.split('.')[-1] if '.' in filename else ''
    file_key = f"{result_key}/{uuid.uuid4()}.{ext}"

    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket' : BUCKET_NAME,
            'Key' : file_key,
            'ContentType' : content_type
        },
        ExpiresIn=expires_in
    )

    return {
        "upload_url": presigned_url,
        "file_key": file_key,
        "expires_in": expires_in
    }
