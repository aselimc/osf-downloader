"""Tests for advanced features and error handling"""

import pytest

from osf_downloader.download import OSFDownloader, OSFError


class TestCustomSettings:
    """Test downloader with custom configuration"""

    def test_custom_settings(self, console, output_dir, project_id, file_path):
        """
        Test downloading with custom downloader settings
        """
        # Custom settings: fewer workers, disable progress
        downloader = OSFDownloader(
            console=console,
            show_progress=False,  # Disable progress bars
            max_workers=4,  # Use 4 concurrent workers
        )

        save_path = output_dir / "custom_download.zip"
        result = downloader.download(project_id, save_path, file_path)

        assert result.exists()
        console.print(
            f"[green]✓[/green] Successfully downloaded with custom settings to: {result}"
        )

    def test_multiple_workers(self, console, output_dir, project_id):
        """Test downloading with different worker counts"""
        for workers in [1, 4, 8]:
            downloader = OSFDownloader(
                console=console, show_progress=False, max_workers=workers
            )

            save_path = output_dir / f"workers_{workers}.zip"
            result = downloader.download(project_id, save_path)

            assert result.exists()
            console.print(
                f"[green]✓[/green] Downloaded with {workers} workers: {result}"
            )


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_project_id(self, console, output_dir):
        """Test error handling for invalid project ID"""
        downloader = OSFDownloader(console=console, show_progress=True)

        save_path = output_dir / "should_fail.zip"

        with pytest.raises(OSFError):
            downloader.download("invalid_id_12345", save_path)

        console.print("[green]✓[/green] Correctly caught error for invalid project ID")

    def test_invalid_file_path(self, console, output_dir, project_id):
        """Test error handling for non-existent file path"""
        downloader = OSFDownloader(console=console, show_progress=True)

        save_path = output_dir / "nonexistent.zip"

        with pytest.raises(OSFError):
            downloader.download(project_id, save_path, "nonexistent/path/file.txt")

        console.print("[green]✓[/green] Correctly caught error for invalid file path")
