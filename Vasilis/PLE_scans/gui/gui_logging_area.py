# copied from matisse code, just with fewer dependencies.

import gui_utils as utils

from datetime import datetime
from queue import Queue

from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor, QFont
from PyQt5.QtWidgets import QTextEdit


class ExitFlag:
    """An empty 'marker' class used to signal a thread with a message queue to gracefully stop."""
    pass


class LoggingThread(QThread):
    """
    A QThread which waits for data to come through a Queue. It blocks until data is available, then sends it to the UI
    thread by emitting a Qt signal. The thread exits when an instance of ExitFlag is pushed to the message queue.

    Note: Any Qt slots implemented in this class will be executed in the creating thread for instances of this class.
    """
    message_received = pyqtSignal(str)

    def __init__(self, queue: Queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue

    def run(self):
        while True:
            message = self.queue.get()
            if isinstance(message, ExitFlag):
                break
            else:
                self.message_received.emit(message)


class LoggingStream:
    """A basic stream-like class with a message queue, meant to replace sys.stdout for logging purposes."""

    def __init__(self, queue: Queue):
        self.queue = queue

    def write(self, message):
        self.queue.put(message)

    def flush(self):
        pass


class LoggingArea(QTextEdit):
    """
    A QTextEdit that can append HTML messages to the end of the text area. Messages that contain the word
    'WARNING' will be colored.

    On initialization, a LoggingThread is started, which emits messages from a queue. Emitted messages from this thread
    are logged to the text area via a Qt slot, which runs in the creating thread for instances of this class.
    """

    FONT_SIZE = 12

    def __init__(self, messages: Queue, *args, **kwargs):
        """
        Parameters
        ----------
        messages
            a message queue. Messages pushed to this queue will be emitted from the LoggingThread and then
            appended to the text area.
        *args
            args to pass to `QTextEdit.__init__`
        **kwargs
            kwargs to pass to `QTextEdit.__init__`
        """

        super().__init__(*args, **kwargs)
        self.messages = messages
        self.setFont(QFont('StyleNormal', self.FONT_SIZE))
        self.update_thread = LoggingThread(messages)
        self.update_thread.message_received.connect(self.log_message)
        self.update_thread.start()

    @pyqtSlot(str)
    def log_message(self, message):
        if 'WARNING' in message:
            message = utils.orange_text(message)

        # Don't print timestamp for just newlines
        if not message.strip():
            timestamp = ''
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S | ")

        self.moveCursor(QTextCursor.End)
        self.insertHtml(timestamp + message.replace('\n', '<br>'))

    def clean_up(self):
        self.messages.put(ExitFlag())
        self.update_thread.wait()
