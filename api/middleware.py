import logging


class LoggingMiddleware():
    logger = logging.getLogger(__name__)

    def process_request(self, req, resp):
        msg = '{m} {u}'.format(m=req.method, u=req.uri)
        self.logger.info(msg)

