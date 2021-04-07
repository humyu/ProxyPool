import logging


# LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
# DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
#
# logging.basicConfig(filename='mylog',filemode='w', level=logging.WARNING, format=LOG_FORMAT, datefmt=DATE_FORMAT)

class Logger:
    @staticmethod
    def get():
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s[:%(lineno)d] - %(message)s")
        logger = logging.getLogger("mylogger")
        logger.setLevel(logging.WARNING)
        # 防止发送重复日志
        if not logger.handlers:
            # 将日志消息发送到输出到Stream，如std.out, std.err或任何file-like对象。
            sh = logging.StreamHandler()
            sh.setFormatter(formatter)
            logger.addHandler(sh)
        return logger
