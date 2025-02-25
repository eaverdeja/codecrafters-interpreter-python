class Return(RuntimeError):
    value: object

    def __init__(self, value):
        self.value = value
