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

- **fileUrl** (required): URL of the archive file to download
- **folderPath** (optional): Output directory (default: `./storage/extracted`)
- **maxFileSizeMb** (optional): Maximum file size in MB (default: 50)
- **fileNamePrefix** (optional): Prefix for extracted file names

## Output

The Actor outputs a dataset with:
- `fileUrl`: The source URL
- `outputPath`: Where files were extracted
- `totalFiles`: Number of extracted files
- `extractedFiles`: Array of all file paths