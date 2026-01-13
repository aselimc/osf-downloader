# src/osf_downloader/download.py

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import requests
from rich.console import Console
from tqdm import tqdm


class OSFError(RuntimeError):
    """Base class for OSF-related errors."""


class OSFRequestError(OSFError):
    pass


class OSFNotFoundError(OSFError):
    pass


class OSFDownloader:
    API_ROOT = "https://api.osf.io/v2"

    def __init__(
        self,
        *,
        console: Optional[Console] = None,
        show_progress: bool = True,
    ) -> None:
        self.console = console or Console()
        self.show_progress = show_progress
        self.session = requests.Session()

    # -------- public API --------

    def download(
        self,
        project_id: str,
        save_path: Path,
        file_path: Optional[str] = None,
    ) -> Path:
        self._status(f"Connecting to OSF project {project_id}")

        node = self._get_json(f"/nodes/{project_id}")
        osfstorage_url = self._get_osfstorage_url(node)

        if file_path:
            download_url = self._resolve_file_path(osfstorage_url, file_path)
        else:
            self._status("Preparing project ZIP")
            download_url = self._zip_url(osfstorage_url)

        save_path = self._resolve_save_path(save_path, file_path)
        self._download_stream(download_url, save_path)

        self._status(f"Saved to {save_path}")
        return save_path

    # -------- OSF navigation --------

    def _get_osfstorage_url(self, node: dict) -> str:
        files_url = node["data"]["relationships"]["files"]["links"]["related"]["href"]
        data = self._get_json_url(files_url)

        for item in data["data"]:
            if item["attributes"]["provider"] == "osfstorage":
                return item["relationships"]["files"]["links"]["related"]["href"]

        raise OSFNotFoundError("osfstorage provider not found")

    def _resolve_file_path(self, root_url: str, path: str) -> str:
        current_url = root_url

        for part in path.split("/"):
            data = self._get_json_url(current_url)

            for item in data["data"]:
                if item["attributes"]["name"] == part:
                    if item["attributes"]["kind"] == "folder":
                        current_url = item["relationships"]["files"]["links"][
                            "related"
                        ]["href"]
                        break
                    return item["links"]["download"]

            else:
                raise OSFNotFoundError(f"Path not found: {part}")

        raise OSFError(f"Path resolves to a folder: {path}")

    # -------- download --------

    def _download_stream(self, url: str, target: Path) -> None:
        target = target.expanduser().resolve()
        os.makedirs(target.parent, exist_ok=True)

        response = self.session.get(url, stream=True)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        chunks = response.iter_content(chunk_size=8192)

        if self.show_progress:
            chunks = tqdm(
                chunks,
                total=total // 8192 if total else None,
                desc=target.name,
                unit="chunk",
                colour="green",
            )

        with open(target, "wb") as f:
            for chunk in chunks:
                if chunk:
                    f.write(chunk)

    # -------- utilities --------

    def _resolve_save_path(self, path: Path, file_path: Optional[str]) -> Path:
        if path.suffix:
            return path
        return path.with_suffix(Path(file_path).suffix if file_path else ".zip")

    def _zip_url(self, osfstorage_url: str) -> str:
        return (
            osfstorage_url.replace("/v2/", "/v1/").replace("nodes", "resources")
            + "?zip="
        )

    def _get_json(self, endpoint: str) -> dict:
        return self._get_json_url(f"{self.API_ROOT}{endpoint}")

    def _get_json_url(self, url: str) -> dict:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise OSFRequestError(str(e)) from e

    def _status(self, message: str) -> None:
        if self.console:
            self.console.print(f"[blue]{message}[/blue]")
