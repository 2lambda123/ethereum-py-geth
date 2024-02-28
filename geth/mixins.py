from __future__ import (
    annotations,
)

import datetime
import logging
import os
import queue
import time
from typing import (
    Any,
    Callable,
    Generator,
)

from geth.utils.filesystem import (
    ensure_path_exists,
)
from geth.utils.thread import (
    spawn,
)
from geth.utils.timeout import (
    Timeout,
)


def construct_logger_file_path(prefix: str, suffix: str) -> str:
    ensure_path_exists("./logs")
    timestamp = datetime.datetime.now().strftime(f"{prefix}-%Y%m%d-%H%M%S-{suffix}.log")
    return os.path.join("logs", timestamp)


def _get_file_logger(name: str, filename: str) -> logging.Logger:
    # create logger with 'spam_application'
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter("%(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


# class JoinableQueue(queue.Queue[Union[bytes, type[StopIteration]]]):
class JoinableQueue(queue.Queue):  # type: ignore
    def __iter__(self) -> Generator[bytes, None, None]:
        while True:
            item = self.get()

            is_stop_iteration_type = isinstance(item, type) and issubclass(
                item, StopIteration
            )
            if isinstance(item, StopIteration) or is_stop_iteration_type:
                return

            elif isinstance(item, Exception):
                raise item

            elif isinstance(item, type) and issubclass(item, Exception):
                raise item

            yield item  # type: ignore

    def join(self, timeout: int | None = None) -> None:
        with Timeout(timeout) as _timeout:
            while not self.empty():
                time.sleep(0)
                _timeout.check()


class InterceptedStreamsMixin:
    """
    Mixin class for GethProcess instances that feeds all of the stdout and
    stderr lines into some set of provided callback functions.
    """

    stdout_callbacks: list[Callable[..., Any]]
    stderr_callbacks: list[Callable[..., Any]]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.stdout_callbacks = []
        self.stdout_queue = JoinableQueue()

        self.stderr_callbacks = []
        self.stderr_queue = JoinableQueue()

    def register_stdout_callback(self, callback_fn: Callable[..., Any]) -> None:
        self.stdout_callbacks.append(callback_fn)

    def register_stderr_callback(self, callback_fn: Callable[..., Any]) -> None:
        self.stderr_callbacks.append(callback_fn)

    def produce_stdout_queue(self) -> None:
        if hasattr(self, "proc"):
            for line in iter(self.proc.stdout.readline, b""):
                self.stdout_queue.put(line)
                time.sleep(0)
        else:
            raise AttributeError("No `proc` attribute found")

    def produce_stderr_queue(self) -> None:
        if hasattr(self, "proc"):
            for line in iter(self.proc.stderr.readline, b""):
                self.stderr_queue.put(line)
                time.sleep(0)
        else:
            raise AttributeError("No `proc` attribute found")

    def consume_stdout_queue(self) -> None:
        for line in self.stdout_queue:
            for fn in self.stdout_callbacks:
                fn(line.strip())
            self.stdout_queue.task_done()
            time.sleep(0)

    def consume_stderr_queue(self) -> None:
        for line in self.stderr_queue:
            for fn in self.stderr_callbacks:
                fn(line.strip())
            self.stderr_queue.task_done()
            time.sleep(0)

    def start(self) -> None:
        # TODO: type ignored bc doesn't know it's always part of BaseGethProcess
        super().start()  # type: ignore

        spawn(self.produce_stdout_queue)
        spawn(self.produce_stderr_queue)

        spawn(self.consume_stdout_queue)
        spawn(self.consume_stderr_queue)

    def stop(self) -> None:
        # TODO: type ignored bc doesn't know it's always part of BaseGethProcess
        super().stop()  # type: ignore

        try:
            self.stdout_queue.put(StopIteration)
            self.stdout_queue.join(5)
        except Timeout:
            pass

        try:
            self.stderr_queue.put(StopIteration)
            self.stderr_queue.join(5)
        except Timeout:
            pass


class LoggingMixin(InterceptedStreamsMixin):
    def __init__(self, *args: Any, **kwargs: Any):
        stdout_logfile_path = kwargs.pop(
            "stdout_logfile_path",
            construct_logger_file_path("geth", "stdout"),
        )
        stderr_logfile_path = kwargs.pop(
            "stderr_logfile_path",
            construct_logger_file_path("geth", "stderr"),
        )

        super().__init__(*args, **kwargs)

        stdout_logger = _get_file_logger("geth-stdout", stdout_logfile_path)
        stderr_logger = _get_file_logger("geth-stderr", stderr_logfile_path)

        self.register_stdout_callback(stdout_logger.info)
        self.register_stderr_callback(stderr_logger.info)
