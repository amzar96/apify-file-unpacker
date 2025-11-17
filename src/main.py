from __future__ import annotations

from apify import Actor
import urllib.request as urllib
import zipfile
import tarfile
import py7zr
import io
import os
from pathlib import Path


def get_mime_type(filename: str) -> str:
    ext = filename.lower().split('.')[-1]
    mime_types = {
        'pdf': 'application/pdf',
        'mp3': 'audio/mpeg',
        'mp4': 'video/mp4',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'svg': 'image/svg+xml',
        'zip': 'application/zip',
        'tar': 'application/x-tar',
        'gz': 'application/gzip',
        '7z': 'application/x-7z-compressed',
        'txt': 'text/plain',
        'html': 'text/html',
        'css': 'text/css',
        'js': 'application/javascript',
        'json': 'application/json',
        'xml': 'application/xml',
        'csv': 'text/csv',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    }
    return mime_types.get(ext, 'application/octet-stream')


def get_file_info(file_url: str) -> dict:
    url_lower = file_url.lower()

    if url_lower.endswith(".zip"):
        return {"format": "zip", "mode": None}
    elif url_lower.endswith((".tar.gz", ".tgz")):
        return {"format": "tar", "mode": "r:gz"}
    elif url_lower.endswith((".tar.bz2", ".tbz2")):
        return {"format": "tar", "mode": "r:bz2"}
    elif url_lower.endswith(".tar"):
        return {"format": "tar", "mode": "r"}
    elif url_lower.endswith(".7z"):
        return {"format": "7z", "mode": None}
    else:
        raise ValueError(f"Unsupported file format: {file_url}")


async def extract_and_store_files(data: bytes, file_url: str) -> list[dict]:
    file_info = get_file_info(file_url)
    format_type = file_info["format"]
    mode = file_info["mode"]

    extracted_files_info = []
    store = await Actor.open_key_value_store()

    try:
        if format_type == "zip":
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                for member in archive.filelist:
                    if not member.is_dir():
                        file_content = archive.read(member.filename)
                        await Actor.set_value(
                            member.filename,
                            file_content,
                            content_type=get_mime_type(member.filename)
                        )
                        download_url = await store.get_public_url(member.filename)
                        extracted_files_info.append({
                            'filename': member.filename,
                            'size': member.file_size,
                            'download_url': download_url,
                            'mime_type': get_mime_type(member.filename)
                        })
                Actor.log.info(f"Extracted {len(extracted_files_info)} files from ZIP archive")

        elif format_type == "tar":
            with tarfile.open(fileobj=io.BytesIO(data), mode=mode) as archive:
                for member in archive.getmembers():
                    if member.isfile():
                        file_content = archive.extractfile(member).read()
                        await Actor.set_value(
                            member.name,
                            file_content,
                            content_type=get_mime_type(member.name)
                        )
                        download_url = await store.get_public_url(member.name)
                        extracted_files_info.append({
                            'filename': member.name,
                            'size': member.size,
                            'download_url': download_url,
                            'mime_type': get_mime_type(member.name)
                        })
                Actor.log.info(f"Extracted {len(extracted_files_info)} files from TAR archive")

        elif format_type == "7z":
            with py7zr.SevenZipFile(io.BytesIO(data), mode="r") as archive:
                all_files = archive.readall()
                for filename, bio in all_files.items():
                    if not filename.endswith('/'):
                        file_content = bio.read()
                        await Actor.set_value(
                            filename,
                            file_content,
                            content_type=get_mime_type(filename)
                        )
                        download_url = await store.get_public_url(filename)
                        file_size = len(file_content)
                        extracted_files_info.append({
                            'filename': filename,
                            'size': file_size,
                            'download_url': download_url,
                            'mime_type': get_mime_type(filename)
                        })
                Actor.log.info(f"Extracted {len(extracted_files_info)} files from 7Z archive")

    except Exception as e:
        Actor.log.error(f"Failed to extract archive: {str(e)}")
        raise

    return extracted_files_info


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}

        file_url = actor_input.get('file_url')

        if not file_url:
            raise ValueError("file_url is required in the input")

        Actor.log.info(f"Ready to unpack file from URL: {file_url}")

        Actor.log.info(f"Downloading file from: {file_url}")

        try:
            with urllib.urlopen(file_url) as response:
                data = response.read()
                Actor.log.info(f"Downloaded {len(data)} bytes")
        except Exception as e:
            Actor.log.error(f"Failed to download file: {str(e)}")
            raise

        extracted_files = await extract_and_store_files(data, file_url)

        Actor.log.info(f"Extraction complete. Files extracted:")
        for file_info in extracted_files[:10]:
            Actor.log.info(f"  - {file_info['filename']} ({file_info['size']} bytes)")
        if len(extracted_files) > 10:
            Actor.log.info(f"  ... and {len(extracted_files) - 10} more files")

        for file_info in extracted_files:
            await Actor.push_data(file_info)

        Actor.log.info(f"Results pushed to dataset: {len(extracted_files)} files extracted")
