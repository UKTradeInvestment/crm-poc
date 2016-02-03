class CDMSException(Exception):
    def __init__(self, message=None, status_code=None):
        super(CDMSException, self).__init__()
        self.message = message
        self.status_code = status_code
