import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.log
import logging

from tornado.options import define, options
import time
import signal
from route import handler
from components.database import async_mysql_client
define("port", default=8000, help="run on the given port", type=int)

class APP:
    def __int__(self):
        self.http_server = None
        self.main_app = None
        self.io_loop = tornado.ioloop.IOLoop.instance()
        self.deadline = None

    def sig_handler(self, sig, frame):  # pylint:disable=W0613
        """
        捕捉停止信号
        :param sig:
        :return:
        """
        logging.info('Caught signal: %s', sig)
        tornado.ioloop.IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        """
        停止app
        :return:
        """
        logging.info('Stopping http server')

        self.http_server.stop()  # 不接收新的 HTTP 请求

        logging.info('Will shutdown in %s seconds ...', 1)

        self.deadline = time.time() + 1
        self.io_loop = tornado.ioloop.IOLoop.current()
        self.stop_loop()

    def stop_loop(self):
        """
        停止主循环
        :return:
        """
        print('Server Shutdown!')
        self.io_loop.stop()

    def init(self):
        """
        初始化app
        :return:
        """
        # register signal.SIGTSTP's handler
        signal.signal(signal.SIGTERM, self.sig_handler)  # 监听终止的信号
        signal.signal(signal.SIGQUIT, self.sig_handler)  # 监听终端退出的信号
        signal.signal(signal.SIGINT, self.sig_handler)  # 连接中断的信号
        signal.signal(signal.SIGTSTP, self.sig_handler)  #
        return True

    def init_log(self):
        logging.info('init log done')
        # logger = logging.getLogger()
        # fmt = tornado.log.LogFormatter(
        #     fmt='%(color)s[%(asctime)s %(funcName)s %(levelname)s]%(end_color)s %(message)s', datefmt='%H:%M:%S')
        # fh = logging.StreamHandler()
        # fh.setFormatter(fmt)
        # fh.setLevel(logging.INFO)
        # logger.addHandler(fh)
        # return logger

    def main_loop(self):
        tornado.options.parse_command_line()
        self.init_log()
        [i.setFormatter(LogFormatter()) for i in logging.getLogger().handlers]
        logging.info('init server...')
        self.main_app = Application()
        self.http_server = tornado.httpserver.HTTPServer(self.main_app)
        self.http_server.listen(options.port)
        logging.info("server running in port %s..." % options.port)
        tornado.ioloop.IOLoop.instance().start()

class LogFormatter(tornado.log.LogFormatter):
    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s[%(asctime)s %(levelname)s]%(end_color)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

class Application(tornado.web.Application):
    def __init__(self):
        handlers = handler
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret="411444270345370dfbb49c29a0f1e3ce",
            login_url="/login",
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)
        logging.info("init Application....")
        self.db = async_mysql_client

if __name__ == "__main__":
    APP = APP()
    if APP.init():
        APP.main_loop()