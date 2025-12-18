from fastapi import APIRouter
from pydantic import BaseModel

from services.s3_service import generated_presigned_url, s3_client, BUCKET_NAME
from services.analyze_service import generate_result_key

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])


class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str


@router.post("/file")
async def upload_file(request: list[PresignedUrlRequest]):
    result = []
    result_key = generate_result_key()
    for r in request:
        result.append(generated_presigned_url(result_key, r.filename, r.content_type))
    return {
        "result_key" : result_key,
        "presigned_url" : result
    }

# result_key를 기준으로 하위 파일 불러오기
def list_files(result_key : str) -> list[dict]:
    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix=f"{result_key}/"
    )

    files = []
    for obj in response.get('Contents', []):
        files.append({
            'file_key': obj['Key'],
            'size': obj['Size'],
            'last_modified': obj['LastModified'].isoformat()
        })

    return files
