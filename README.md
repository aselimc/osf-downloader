# osf-downloader

Download files (or a ZIP of an entire project) from the **Open Science Framework (OSF)** from the command line. Useful for pulling OSF-hosted datasets into local workflows and CI pipelines.

## Features

- Download an OSF project/component by ID (as a ZIP)
- Download a single file by its path inside OSF storage
- Simple CLI suitable for scripting

## Install

### Option A: From source (recommended for development)

```bash
git clone https://github.com/aselimc/osf-downloader.git
cd osf-downloader
# editable install
pip install -e .
```

### Option B: Python package

```bash
pip install osf-downloader
```

Requirements:

- Python 3.9+

## Usage

The installed CLI entrypoint is `osf-download`.

> Replace `<OSF_ID>` with your OSF project or component id (the short code in the OSF URL).

```bash
osf-download download <OSF_ID> ./data
```

Download a single file by path inside OSF storage:

```bash
osf-download download <OSF_ID> ./data/myfile.csv path/inside/osf/myfile.csv
```

- Command shape: `osf-download download PROJECT_ID SAVE_PATH [FILE_PATH]`.
- `file_path` is the path inside **osfstorage** (case-sensitive; use `/` separators).
- `save_path` is treated as an *output file path* if it already has a suffix/extension.
- If `save_path` has **no** suffix/extension, the tool appends one automatically:
    - project download → `.zip`
    - file download → uses the extension from `file_path` (e.g. `.csv`)


## License

MIT. See `LICENSE`.
