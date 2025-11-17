## File Unpacker

Downloads and extracts archive files from URLs. Supports multiple archive formats and outputs the list of extracted files to a dataset.

## Features

- **Multiple formats**: ZIP, TAR, TAR.GZ, TAR.BZ2, and 7Z
- **Simple input**: Just provide a URL to the archive file
- **Dataset output**: Returns a list of all extracted files

## How it works

1. Provide a URL to an archive file
2. The Actor downloads and extracts the file
3. Results are saved to a dataset with file paths and metadata

## Input

- **file_url** (required): URL of the archive file to download
- **folder_path** (optional): Output directory (default: `./storage/extracted`)
- **max_file_size_mb** (optional): Maximum file size in MB (default: 50)
- **file_name_prefix** (optional): Prefix for extracted file names

## Output

The Actor outputs a dataset with one record per extracted file containing:
- `file_url`: The source archive URL
- `output_path`: Where files were extracted
- `extracted_file`: Path to the individual extracted file
- `max_file_size_mb`: Maximum file size setting used
- `file_name_prefix`: File name prefix (if provided)

## Example Input

```json
{
  "file_url": "https://example.com/archive.zip",
  "folder_path": "./storage/extracted",
  "max_file_size_mb": 50
}
```

## Example Output

```json
{
  "file_url": "https://example.com/archive.zip",
  "output_path": "storage/extracted",
  "extracted_file": "storage/extracted/myfile.txt",
  "max_file_size_mb": 50,
  "file_name_prefix": null
}
```