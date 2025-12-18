import boto3
from botocore.config import Config
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

# .env 파일의 환경변수 이름과 일치시킴
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('S3_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
    config=Config(signature_version='s3v4')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME')


def list_files_in_prefix(prefix: str) -> list[str]:
    """
    S3 버킷의 특정 prefix에 있는 모든 파일 키를 가져옵니다.
    """
    keys = []
    try:
        # The prefix should end with a '/' to act like a folder
        if not prefix.endswith('/'):
            prefix += '/'

        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=prefix)

        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    keys.append(obj['Key'])
        return keys
    except Exception as e:
        print(f"Error listing files from S3: {e}")
        return []


def generated_presigned_url(result_key: str, filename: str, content_type: str, expires_in=3600) -> dict:
    """
    Presigned URL을 생성합니다. analyze_router의 로직과 일치하도록 키 생성을 수정했습니다.
    """
    # router에서 사용하는 키 형식과 일치시킴
    file_key = f"{result_key}/{filename}"

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
