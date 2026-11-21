"""Upload the build folder to the S3 bucket (RustFS on vm1, through an SSH tunnel). Build tool only: needs boto3.

MP3 files are immutable (their URL carries the hash), manifests are written last and never cached, so the backend
never sees a manifest that points to a file that is not there yet.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

POLICY_FILE = Path(__file__).resolve().parents[3] / "deploy" / "vm1" / "storage" / "mezon-audio.policy.json"


def make_client(endpoint: str, access_key: str, secret_key: str):
    import boto3
    from botocore.config import Config

    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="us-east-1",
        config=Config(s3={"addressing_style": "path"}, signature_version="s3v4", retries={"max_attempts": 3}),
    )


def init_bucket(s3, bucket: str, policy_file: Path = POLICY_FILE, log: Callable[[str], None] = print) -> None:
    """Create the bucket (idempotent) and allow anonymous GET on scenarios/ and common/ only."""
    from botocore.exceptions import ClientError

    try:
        s3.head_bucket(Bucket=bucket)
        log(f"bucket {bucket} exists")
    except ClientError:
        s3.create_bucket(Bucket=bucket)
        log(f"bucket {bucket} created")
    try:
        s3.put_public_access_block(
            Bucket=bucket,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True, "IgnorePublicAcls": True,
                "BlockPublicPolicy": False, "RestrictPublicBuckets": False,
            },
        )
    except ClientError as exc:  # not every S3 server implements it; the policy below is what matters
        log(f"public access block not set ({exc.response['Error'].get('Code')})")
    s3.put_bucket_policy(Bucket=bucket, Policy=policy_file.read_text(encoding="utf-8"))
    log(f"read-only public policy applied from {policy_file.name}")


def _remote_manifest(s3, bucket: str, key: str) -> dict:
    from botocore.exceptions import ClientError

    try:
        return json.loads(s3.get_object(Bucket=bucket, Key=key)["Body"].read()).get("lines", {})
    except (ClientError, ValueError):
        return {}


def upload(s3, bucket: str, out_dir: Path, prune: bool = False, log: Callable[[str], None] = print) -> dict[str, int]:
    stats = {"uploaded": 0, "unchanged": 0, "deleted": 0, "manifests": 0}
    for mfile in sorted(out_dir.glob("scenarios/*/*/manifest.json")):
        mkey = mfile.relative_to(out_dir).as_posix()
        local = json.loads(mfile.read_text(encoding="utf-8"))["lines"]
        remote = _remote_manifest(s3, bucket, mkey)
        for key, entry in local.items():
            if remote.get(key, {}).get("hash") == entry["hash"]:
                stats["unchanged"] += 1
                continue
            s3.put_object(
                Bucket=bucket, Key=entry["path"], Body=(out_dir / entry["path"]).read_bytes(),
                ContentType="audio/mpeg", CacheControl="public, max-age=31536000, immutable",
            )
            stats["uploaded"] += 1
        s3.put_object(
            Bucket=bucket, Key=mkey, Body=mfile.read_bytes(),
            ContentType="application/json", CacheControl="no-cache",
        )
        stats["manifests"] += 1
        log(f"{mkey}: {len(local)} lines")
        if prune:
            keep = {e["path"] for e in local.values()} | {mkey}
            prefix = mkey.rsplit("/", 1)[0] + "/"
            for page in s3.get_paginator("list_objects_v2").paginate(Bucket=bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    if obj["Key"] not in keep:
                        s3.delete_object(Bucket=bucket, Key=obj["Key"])
                        stats["deleted"] += 1
    return stats
