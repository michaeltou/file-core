from engine.util.log.LogUtil import LogUtil


def debug(msg, *args, **kwargs):
    LogUtil.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    LogUtil.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    LogUtil.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    LogUtil.error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    LogUtil.critical(msg, *args, **kwargs)


