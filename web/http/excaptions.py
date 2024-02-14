class EmptyHttp(Exception):
    def __init__(self):
        super().__init__('Empty http.')


class HttpSyntaxError(Exception):
    def __init__(self):
        super().__init__('Http syntax error.')
