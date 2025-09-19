"""Tests for spinner utility."""

from unittest.mock import Mock, patch

from workato_platform.cli.utils.spinner import Spinner


class TestSpinner:
    """Test the Spinner utility class."""

    def test_spinner_initialization(self):
        """Test Spinner can be initialized."""
        spinner = Spinner("Loading...")
        assert spinner.message == "Loading..."

    def test_spinner_message_attribute(self):
        """Test Spinner stores message correctly."""
        spinner = Spinner("Processing...")
        assert spinner.message == "Processing..."

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
            assert spinner.running is True

            elapsed_time = spinner.stop()
            assert spinner.running is False
            assert isinstance(elapsed_time, float)

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
            assert spinner.message == message

    def test_spinner_thread_safety(self):
        """Test that spinner handles threading correctly."""
        with patch("workato_platform.cli.utils.spinner.threading.Thread") as mock_thread:
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance

            spinner = Spinner("Testing...")

            # Test that it has a message lock for thread safety
            assert hasattr(spinner, '_message_lock')

            spinner.start()
            # Should create thread
            mock_thread.assert_called_once()

            # Test message update with thread safety
            spinner.update_message("New message")
            assert spinner.message == "New message"

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

            # Should not raise exception when dealing with stdout operations
            spinner.start()
            spinner.stop()

            # Verify stdout operations were attempted
            assert mock_stdout.write.called
            assert mock_stdout.flush.called

    @patch("workato_platform.cli.utils.spinner.sys.stdout")
    def test_spinner_stop_without_start(self, mock_stdout):
        """Stop without starting should return zero elapsed time."""
        spinner = Spinner("No start")
        elapsed = spinner.stop()

        assert elapsed == 0
        mock_stdout.write.assert_called()
        mock_stdout.flush.assert_called()

    def test_spinner_message_update(self):
        """Test that spinner can update its message dynamically."""
        spinner = Spinner("Initial message")
        assert spinner.message == "Initial message"

        spinner.update_message("Updated message")
        assert spinner.message == "Updated message"
