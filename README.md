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
# install using your project’s preferred tool (pip/poetry/pipx/etc.)
```

### Option B: Python package (if published)

```bash
pip install osf-downloader
```

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

Notes:

- `save_path` can be a directory or a filename.
- If `save_path` is a directory, the tool will choose a filename automatically:
    - project download → `*.zip`
    - file download → uses the file extension from `file_path`


## Examples

Download an OSF project ZIP to `./datasets/osf.zip`:

```bash
osf-download download abcd1 ./datasets/osf.zip
```

Download an OSF project ZIP into the current directory (filename is chosen automatically):

```bash
osf-download download abcd1 .
```

Download a single file into `./datasets/`:

```bash
osf-download download abcd1 ./datasets results/data.csv
```


## Troubleshooting

- **404 / not found**: verify the OSF id and that the project/component is public.
- **401 / unauthorized**: this tool currently does not handle OSF authentication; use public resources.
- **Path not found**: if downloading a single file, ensure `file_path` matches the OSF storage path (case-sensitive).

## Contributing

Issues and pull requests are welcome. Include:

- A clear description of the OSF resource and expected behavior
- Minimal reproduction steps
- Logs/trace output if available

## License

MIT. See `LICENSE`.
