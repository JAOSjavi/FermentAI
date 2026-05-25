import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from app.config import settings

_s3 = None


def get_s3():
    global _s3
    if _s3 is None:
        protocol = "https" if settings.MINIO_SECURE else "http"
        _s3 = boto3.client(
            "s3",
            endpoint_url=f"{protocol}://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )
    return _s3


def ensure_bucket():
    s3 = get_s3()
    try:
        s3.head_bucket(Bucket=settings.MINIO_BUCKET)
    except ClientError:
        s3.create_bucket(Bucket=settings.MINIO_BUCKET)
        # Política de lectura pública para URLs pre-firmadas sin bloqueo CORS
        import json
        policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{settings.MINIO_BUCKET}/*"],
            }],
        }
        s3.put_bucket_policy(
            Bucket=settings.MINIO_BUCKET,
            Policy=json.dumps(policy),
        )


def upload_file(local_path: str, object_key: str) -> str:
    s3 = get_s3()
    s3.upload_file(local_path, settings.MINIO_BUCKET, object_key)
    return object_key


def upload_bytes(data: bytes, object_key: str, content_type: str = "image/jpeg"):
    s3 = get_s3()
    import io
    s3.upload_fileobj(io.BytesIO(data), settings.MINIO_BUCKET, object_key,
                      ExtraArgs={"ContentType": content_type})
    return object_key


def presigned_url(object_key: str, expires: int = 3600) -> str:
    s3 = get_s3()
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.MINIO_BUCKET, "Key": object_key},
            ExpiresIn=expires,
        )
        # Reemplaza el endpoint interno por el público (necesario en Docker)
        protocol = "https" if settings.MINIO_SECURE else "http"
        internal = f"{protocol}://{settings.MINIO_ENDPOINT}"
        public = f"{protocol}://{settings.MINIO_PUBLIC_ENDPOINT}"
        return url.replace(internal, public, 1)
    except ClientError:
        return ""


def delete_prefix(prefix: str):
    s3 = get_s3()
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=settings.MINIO_BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            s3.delete_object(Bucket=settings.MINIO_BUCKET, Key=obj["Key"])


def copy_prefix(src_prefix: str, dst_prefix: str):
    s3 = get_s3()
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=settings.MINIO_BUCKET, Prefix=src_prefix):
        for obj in page.get("Contents", []):
            new_key = dst_prefix + obj["Key"][len(src_prefix):]
            s3.copy_object(
                Bucket=settings.MINIO_BUCKET,
                CopySource={"Bucket": settings.MINIO_BUCKET, "Key": obj["Key"]},
                Key=new_key,
            )


def delete_object(key: str):
    s3 = get_s3()
    s3.delete_object(Bucket=settings.MINIO_BUCKET, Key=key)


def list_objects(prefix: str) -> list[str]:
    s3 = get_s3()
    keys: list[str] = []
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=settings.MINIO_BUCKET, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.append(obj["Key"])
    return keys


def get_bytes(key: str) -> bytes:
    s3 = get_s3()
    response = s3.get_object(Bucket=settings.MINIO_BUCKET, Key=key)
    return response["Body"].read()
