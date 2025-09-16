import sys
import threading
import time


class Spinner:
    """Simple spinner animation with elapsed time counter for CLI"""

    def __init__(self, message: str = "Loading") -> None:
        self.message = message
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.running = False
        self.thread: threading.Thread | None = None
        self.start_time = 0.0
        self._message_lock = threading.Lock()  # Thread safety for message updates

    def start(self) -> None:
        self.running = True
        self.start_time = time.time()
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()

    def stop(self) -> float:
        self.running = False
        if self.thread:
            self.thread.join()
        # Clear the line
        max_line_length = (
            len(self.message) + 20
        )  # Account for spinner, time, and padding
        sys.stdout.write("\r" + " " * max_line_length + "\r")
        sys.stdout.flush()

        # Return elapsed time
        if self.start_time:
            return time.time() - self.start_time
        return 0

    def update_message(self, new_message: str) -> None:
        """Update the spinner message while it's running"""
        with self._message_lock:
            self.message = new_message

    def _spin(self) -> None:
        idx = 0
        while self.running:
            char = self.spinner_chars[idx % len(self.spinner_chars)]
            elapsed = time.time() - self.start_time
            elapsed_str = f"{elapsed:.1f}s"

            # Format: spinner + message + elapsed time
            # Use lock to safely read the message
            with self._message_lock:
                current_message = self.message
            display_text = f"{char} {current_message}... ({elapsed_str})"

            # Use carriage return to overwrite the line
            # This is simpler and more reliable than trying to clear with spaces
            sys.stdout.write(f"\r{display_text}")
            sys.stdout.flush()
            time.sleep(0.1)
            idx += 1
