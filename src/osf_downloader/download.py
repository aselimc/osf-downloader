# src/osf_downloader/download.py

from __future__ import annotations

import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock
from typing import Any, Iterable, Optional

import requests
from rich.console import Console
from tqdm import tqdm


class OSFError(RuntimeError):
    pass


class OSFRequestError(OSFError):
    pass


class OSFNotFoundError(OSFError):
    pass


_tqdm_lock = Lock()


class OSFDownloader:
    API_ROOT = "https://api.osf.io/v2"

    _TQDM_COLOURS = [
        "green",
        "cyan",
        "magenta",
        "yellow",
        "blue",
        "red",
        "white",
    ]

    def __init__(
        self,
        *,
        console: Optional[Console] = None,
        show_progress: bool = True,
        max_workers: int = 8,
    ) -> None:
        self.console = console or Console()
        self.show_progress = show_progress
        self.max_workers = max_workers
        self.session = requests.Session()

    # =======================
    # Public API
    # =======================

    def download(
        self,
        project_id: str,
        save_path: Path,
        file_path: Optional[str] = None,
    ) -> Path:
        self._status(f"Connecting to OSF project {project_id}")

        node = self._get_json(f"/nodes/{project_id}")
        root_url = self._get_osfstorage_url(node)

        save_path = self._resolve_save_path(save_path, file_path)

        if file_path:
            url = self._resolve_file_path(root_url, file_path)
            self._download_single(url, save_path)
        else:
            self._status("Listing all files in osfstorage")
            files = list(self._walk_files(root_url))
            self._download_all_to_zip(files, save_path)

        self._status(f"Saved to {save_path}")
        return save_path

    # =======================
    # OSF traversal
    # =======================

    def _get_osfstorage_url(self, node: dict) -> str:
        files_url = node["data"]["relationships"]["files"]["links"]["related"]["href"]
        data = self._get_json_url(files_url)

        for item in data["data"]:
            if item["attributes"]["provider"] == "osfstorage":
                return item["relationships"]["files"]["links"]["related"]["href"]

        raise OSFNotFoundError("osfstorage provider not found")

    def _walk_files(self, url: str, prefix: str = "") -> Iterable[tuple[str, str]]:
        data = self._get_json_url(url)

        for item in data["data"]:
            name = item["attributes"]["name"]
            kind = item["attributes"]["kind"]

            if kind == "file":
                yield item["links"]["download"], f"{prefix}{name}"
            else:
                next_url = item["relationships"]["files"]["links"]["related"]["href"]
                yield from self._walk_files(next_url, f"{prefix}{name}/")

    def _resolve_file_path(self, root_url: str, path: str) -> str:
        current = root_url
        for part in path.split("/"):
            data = self._get_json_url(current)
            for item in data["data"]:
                if item["attributes"]["name"] == part:
                    if item["attributes"]["kind"] == "folder":
                        current = item["relationships"]["files"]["links"]["related"][
                            "href"
                        ]
                        break
                    return item["links"]["download"]
            else:
                raise OSFNotFoundError(f"Path not found: {part}")
        raise OSFError(f"Path resolves to a folder: {path}")

    # =======================
    # Download logic
    # =======================

    def _download_single(self, url: str, target: Path) -> None:
        response = self.session.get(url, stream=True)
        response.raise_for_status()

        os.makedirs(target.parent, exist_ok=True)

        total = int(response.headers.get("content-length", 0))
        chunks = response.iter_content(chunk_size=8192)

        with open(target, "wb") as f:
            if not self.show_progress:
                for chunk in chunks:
                    if chunk:
                        f.write(chunk)
                return

            with self._tqdm(
                total=total or None,
                desc=target.name,
                leave=True,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                colour=self._TQDM_COLOURS[0],
            ) as bar:
                for chunk in chunks:
                    if chunk:
                        f.write(chunk)
                        bar.update(len(chunk))

    def _download_all_to_zip(
        self,
        files: list[tuple[str, str]],
        target: Path,
    ) -> None:
        os.makedirs(target.parent, exist_ok=True)

        bars: list[tqdm] = []

        for i, (_, arcname) in enumerate(files):
            bars.append(
                self._tqdm(
                    total=0,
                    desc=arcname,
                    position=i,
                    leave=False,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    colour=self._TQDM_COLOURS[i % len(self._TQDM_COLOURS)],
                )
            )

        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                futures = [
                    pool.submit(self._fetch_file_streamed, url, arcname, bar)
                    for (url, arcname), bar in zip(files, bars)
                ]

                for future in as_completed(futures):
                    arcname, data = future.result()
                    zf.writestr(arcname, data)

        for bar in bars:
            bar.close()

    def _fetch_file_streamed(
        self,
        url: str,
        arcname: str,
        bar: tqdm,
    ) -> tuple[str, bytes]:
        response = self.session.get(url, stream=True)
        response.raise_for_status()

        total = int(response.headers.get("content-length", 0))
        bar.reset(total=total or None)

        chunks: list[bytes] = []

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                chunks.append(chunk)
                with _tqdm_lock:
                    bar.update(len(chunk))

        return arcname, b"".join(chunks)

    def _tqdm(self, *args: Any, **kwargs: Any) -> tqdm:
        """Create a tqdm progress bar with optional colour.

        tqdm's `colour` kwarg isn't available in all versions; this wrapper
        keeps the CLI working on older tqdm versions by retrying without it.
        """

        kwargs.setdefault("disable", not self.show_progress)

        try:
            return tqdm(*args, **kwargs)
        except TypeError:
            if "colour" not in kwargs:
                raise
            kwargs.pop("colour", None)
            return tqdm(*args, **kwargs)

    # =======================
    # Utilities
    # =======================

    def _resolve_save_path(self, path: Path, file_path: Optional[str]) -> Path:
        if path.suffix:
            return path
        return path.with_suffix(Path(file_path).suffix if file_path else ".zip")

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
