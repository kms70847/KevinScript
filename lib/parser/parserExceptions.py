class NoActionFoundError(Exception):
    def __init__(self, token):
        Exception.__init__(self, "Couldn't parse string - no action found for {}".format(token))
        self.token = token