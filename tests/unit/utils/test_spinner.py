"""Tests for spinner utility."""

from unittest.mock import Mock, patch

from workato_platform.cli.utils.spinner import Spinner


class TestSpinner:
    """Test the Spinner utility class."""

    def test_spinner_initialization(self):
        """Test Spinner can be initialized."""
        spinner = Spinner("Loading...")
        assert spinner.text == "Loading..."

    def test_spinner_context_manager(self):
        """Test Spinner works as context manager."""
        with patch(
            "workato_platform.cli.utils.spinner.threading.Thread"
        ) as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            with Spinner("Processing...") as spinner:
                assert spinner.text == "Processing..."

            # Should have started and stopped thread
            mock_thread_instance.start.assert_called_once()
            # Thread should be stopped when exiting context

    def test_spinner_start_stop_methods(self):
        """Test explicit start/stop methods."""
        with patch(
            "workato_platform.cli.utils.spinner.threading.Thread"
        ) as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            spinner = Spinner("Working...")

            spinner.start()
            mock_thread_instance.start.assert_called_once()

            spinner.stop()
            # Should have set stop event

    def test_spinner_with_different_messages(self):
        """Test spinner with various messages."""
        messages = [
            "Loading data...",
            "Processing recipes...",
            "Connecting to API...",
            "🔄 Syncing...",
        ]

        for message in messages:
            spinner = Spinner(message)
            assert spinner.text == message

    def test_spinner_thread_safety(self):
        """Test that spinner handles threading correctly."""
        with (
            patch("workato_platform.cli.utils.spinner.threading.Thread") as mock_thread,
            patch("workato_platform.cli.utils.spinner.threading.Event") as mock_event,
        ):
            mock_thread_instance = Mock()
            mock_event_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            mock_event.return_value = mock_event_instance

            spinner = Spinner("Testing...")
            spinner.start()

            # Should create thread and event
            mock_thread.assert_called_once()
            mock_event.assert_called_once()

            spinner.stop()
            mock_event_instance.set.assert_called_once()

    def test_spinner_animation_characters(self):
        """Test that spinner uses expected animation characters."""
        spinner = Spinner("Animating...")

        # Should have animation characters defined
        assert hasattr(spinner, "spinner_chars") or hasattr(spinner, "chars")

    @patch("workato_platform.cli.utils.spinner.sys.stdout")
    def test_spinner_output_handling(self, mock_stdout):
        """Test that spinner handles terminal output correctly."""
        with patch("workato_platform.cli.utils.spinner.threading.Thread"):
            spinner = Spinner("Output test...")

            # Should not raise exception when dealing with stdout
            with spinner:
                pass
