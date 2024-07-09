import logging

VERBOSE_LOG = os.environ.get('VERBOSE_LOG', 'off').lower() == 'on'
TRACE_LOG_LEVEL_NUM = 9
logging.addLevelName(TRACE_LOG_LEVEL_NUM, "TRACE")
log_console_formatter = logging.Formatter(
    "[%(asctime)s][%(threadName)s] %(levelname)-7.7s - %(message)s", datefmt='%H:%M:%S')
stdout_console_handler = logging.StreamHandler(sys.stdout)
stdout_console_handler.setFormatter(log_console_formatter)
stdout_console_handler.addFilter(_StdoutFilter())
stdout_console_handler.setLevel(logging.INFO)
stderr_console_handler = logging.StreamHandler(sys.stderr)
stderr_console_handler.setFormatter(log_console_formatter)
stderr_console_handler.setLevel(logging.WARNING)

def get_logger(name):
    """
    Retrieve logger by name which has console handler added
    (stdout for DEBUG and INFO and stderr for WARN, ERROR, CRITICAL)
    :param name: Logger name, usually the module name
    :return: the logger
    """
    _logger = logging.getLogger('temp')
    logger = _logger.getChild(name)
    if not any([handler for handler in _logger.handlers if handler == stdout_console_handler]):
        _logger.addHandler(stdout_console_handler)
        _logger.addHandler(stderr_console_handler)
    logger.filters = _logger.filters
    return logger

def init_logging(file=None, verbose=False, log_filter=None):
    """
    Initialize logging:
    - Log file configuration
    - Set level to debug for log file
    - Set level to debug for console if verbose is true, otherwise INFO as default
    :param verbose:
    :param file:
    :param log_filter:  global default log filter
    :return:
    """
    final_verbose = verbose or VERBOSE_LOG
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    logging.getLogger('__main__').setLevel(TRACE_LOG_LEVEL_NUM if final_verbose else logging.DEBUG)
    _logger = logging.getLogger('temp')
    if log_filter is not None:
        _logger.addFilter(log_filter)
    _logger.setLevel(TRACE_LOG_LEVEL_NUM if final_verbose else logging.DEBUG)
    log_file_formatter = logging.Formatter(
        "[%(asctime)s][%(threadName)s] %(levelname)-7.7s - %(message)s")
    log_file_formatter.converter = time.gmtime

    def trace(self, message, *args, **kws):
        if self.isEnabledFor(TRACE_LOG_LEVEL_NUM):
            # Yes, logger takes its '*args' as 'args'.
            self._log(TRACE_LOG_LEVEL_NUM, message, args, **kws)

    def error(self, msg, *args, **kwargs):
        if self.isEnabledFor(TRACE_LOG_LEVEL_NUM) and sys.exc_info() != (None, None, None):
            self._log(TRACE_LOG_LEVEL_NUM, msg, args, exc_info=True)
        if self.isEnabledFor(logging.ERROR):
            self._log(logging.ERROR, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        if self.isEnabledFor(TRACE_LOG_LEVEL_NUM) and sys.exc_info() != (None, None, None):
            self._log(TRACE_LOG_LEVEL_NUM, msg, args, exc_info=True)
        if self.isEnabledFor(logging.WARNING):
            self._log(logging.WARNING, msg, args, **kwargs)

    logging.Logger.trace = trace
    logging.Logger.error = error
    logging.Logger.warning = warning

    if file is not None:
        _Global_vars.log_file = file
        file_handler = logging.FileHandler(_Global_vars.log_file, encoding='utf-8', delay=True)
        file_handler.setFormatter(log_file_formatter)
        file_handler.setLevel(TRACE_LOG_LEVEL_NUM if final_verbose else logging.DEBUG)
        root_logger.addHandler(file_handler)

    stdout_console_handler.setLevel(logging.DEBUG if final_verbose else logging.INFO)
