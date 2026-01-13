"""Tests for core download functionality"""

from osf_downloader.download import OSFDownloader


class TestProjectDownload:
    """Test downloading entire OSF projects"""

    def test_download_entire_project(self, console, output_dir, project_id):
        """
        Test downloading entire OSF project as ZIP
        (as described in README: osf-download download <OSF_ID> ./data)
        """
        downloader = OSFDownloader(console=console, show_progress=True)

        save_path = output_dir / "project.zip"
        result = downloader.download(project_id, save_path)

        assert result.exists()
        assert result.suffix == ".zip"
        console.print(f"[green]✓[/green] Successfully downloaded project to: {result}")

    def test_download_project_auto_extension(self, console, output_dir, project_id):
        """
        Test downloading project where .zip extension is chosen automatically
        (as described in README: osf-download download abcd1 ./datasets/osf)
        """
        downloader = OSFDownloader(console=console, show_progress=True)

        save_path = output_dir / "project_auto"
        result = downloader.download(project_id, save_path)

        assert result.exists()
        console.print(f"[green]✓[/green] Successfully downloaded project to: {result}")


class TestFileDownload:
    """Test downloading individual files from OSF storage"""

    def test_download_single_file(self, console, output_dir, project_id, file_path):
        """
        Test downloading a single file by its path inside OSF storage
        (as described in README: osf-download download <OSF_ID> ./data/myfile.csv path/inside/osf/myfile.csv)
        """
        downloader = OSFDownloader(console=console, show_progress=True)

        filename = file_path.split("/")[-1]
        save_path = output_dir / f"{filename}.zip"
        result = downloader.download(project_id, save_path, file_path)

        assert result.exists()
        console.print(f"[green]✓[/green] Successfully downloaded file to: {result}")

    def test_download_single_file_to_directory(
        self, console, output_dir, project_id, file_path
    ):
        """
        Test downloading a single file into a directory
        (as described in README: osf-download download abcd1 ./datasets results/data.csv)
        """
        downloader = OSFDownloader(console=console, show_progress=True)

        filename = file_path.split("/")[-1]
        save_path = output_dir / filename
        result = downloader.download(project_id, save_path, file_path)

        assert result.exists()
        console.print(f"[green]✓[/green] Successfully downloaded file to: {result}")
        assert result.exists()
        console.print(f"[green]✓[/green] Successfully downloaded file to: {result}")
        assert result.exists()
        console.print(f"[green]✓[/green] Successfully downloaded file to: {result}")
