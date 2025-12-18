from pydantic import BaseModel


class File(BaseModel):
    file_name: str
    content_type: str

class RequestAnalyze(BaseModel):
    jd_url: str
    files: list[File]



