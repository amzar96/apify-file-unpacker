from __future__ import annotations

from apify import Actor
import urllib.request as urllib
import zipfile
import tarfile
import py7zr
import io
from pathlib import Path


def extract_archive(data: bytes, file_url: str, output_dir: Path) -> list[str]:
    extracted_files = []
    output_dir.mkdir(parents=True, exist_ok=True)

    url_lower = file_url.lower()

    try:
        if url_lower.endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                zf.extractall(output_dir)
                extracted_files = [str(output_dir / name) for name in zf.namelist()]
                Actor.log.info(
                    f"Extracted {len(extracted_files)} files from ZIP archive"
                )

        elif url_lower.endswith((".tar.gz", ".tgz")):
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
                tf.extractall(output_dir)
                extracted_files = [
                    str(output_dir / member.name) for member in tf.getmembers()
                ]
                Actor.log.info(
                    f"Extracted {len(extracted_files)} files from TAR.GZ archive"
                )

        elif url_lower.endswith((".tar.bz2", ".tbz2")):
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:bz2") as tf:
                tf.extractall(output_dir)
                extracted_files = [
                    str(output_dir / member.name) for member in tf.getmembers()
                ]
                Actor.log.info(
                    f"Extracted {len(extracted_files)} files from TAR.BZ2 archive"
                )

        elif url_lower.endswith(".tar"):
            with tarfile.open(fileobj=io.BytesIO(data), mode="r") as tf:
                tf.extractall(output_dir)
                extracted_files = [
                    str(output_dir / member.name) for member in tf.getmembers()
                ]
                Actor.log.info(
                    f"Extracted {len(extracted_files)} files from TAR archive"
                )

        elif url_lower.endswith(".7z"):
            with py7zr.SevenZipFile(io.BytesIO(data), mode="r") as szf:
                szf.extractall(output_dir)
                extracted_files = [str(output_dir / name) for name in szf.getnames()]
                Actor.log.info(
                    f"Extracted {len(extracted_files)} files from 7Z archive"
                )
        else:
            raise ValueError(f"Unsupported file format: {file_url}")

    except Exception as e:
        Actor.log.error(f"Failed to extract archive: {str(e)}")
        raise

    return extracted_files


async def download_and_extract_file(file_url: str, output_dir: Path) -> list[str]:
    Actor.log.info(f"Downloading file from: {file_url}")

    try:
        with urllib.urlopen(file_url) as response:
            data = response.read()
            Actor.log.info(f"Downloaded {len(data)} bytes")

        extracted_files = extract_archive(data, file_url, output_dir)

        Actor.log.info(
            f"Successfully extracted {len(extracted_files)} files to {output_dir}"
        )
        return extracted_files

    except Exception as e:
        Actor.log.error(f"Failed to download and extract file: {str(e)}")
        raise


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}

        file_url = actor_input.get('fileUrl')
        folder_path = actor_input.get('folderPath', './storage/extracted')
        max_file_size_mb = actor_input.get('maxFileSizeMb', 50)
        file_name_prefix = actor_input.get('fileNamePrefix')

        if not file_url:
            raise ValueError("fileUrl is required in the input")

        Actor.log.info(f"Ready to unpack file from URL: {file_url}")

        output_dir = Path(folder_path)

        extracted_files = await download_and_extract_file(file_url, output_dir)

        Actor.log.info(f"Extraction complete. Files extracted:")
        for file_path in extracted_files[:10]:
            Actor.log.info(f"  - {file_path}")
        if len(extracted_files) > 10:
            Actor.log.info(f"  ... and {len(extracted_files) - 10} more files")

        for file_path in extracted_files:
            result = {
                'fileUrl': file_url,
                'outputPath': str(output_dir),
                'extractedFile': file_path,
                'maxFileSizeMb': max_file_size_mb,
                'fileNamePrefix': file_name_prefix
            }
            await Actor.push_data(result)

        Actor.log.info(f"Results pushed to dataset: {len(extracted_files)} files extracted")
