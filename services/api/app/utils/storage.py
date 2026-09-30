"""S3-compatible storage abstraction using boto3."""
import uuid
from pathlib import PurePosixPath

import boto3
from botocore.exceptions import ClientError

from ..config import settings


def _get_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.storage_endpoint,
        aws_access_key_id=settings.storage_access_key,
        aws_secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region,
    )


def upload_file(file_bytes: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
    """Upload bytes to storage and return the object URI."""
    client = _get_client()
    key = f"evidence/{uuid.uuid4()}/{filename}"
    client.put_object(
        Bucket=settings.storage_bucket,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return f"s3://{settings.storage_bucket}/{key}"


def generate_presigned_url(uri: str, expires_in: int = 3600) -> str:
    """Generate a presigned download URL for a stored object."""
    client = _get_client()
    bucket, key = _parse_uri(uri)
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def _parse_uri(uri: str) -> tuple[str, str]:
    """Parse s3://bucket/key into (bucket, key)."""
    without_scheme = uri[len("s3://"):]
    bucket, _, key = without_scheme.partition("/")
    return bucket, key
