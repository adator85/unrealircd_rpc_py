
class RpcConnectionError(Exception):

    def __init__(self, detail: str, returncode: int = -1):
        self.returncode: int = returncode
        detail = detail.strip()
        super().__init__(detail)


class RpcInvalidUrlFormat(Exception):

    def __init__(self, detail: str, returncode: int = -1):
        self.returncode: int = returncode
        detail = detail.strip()
        super().__init__(detail)


class RpcUnixSocketFileNotFoundError(Exception):

    def __init__(self, detail: str, returncode: int = -1):
        self.returncode: int = returncode
        detail = detail.strip()
        super().__init__(detail)


class RpcProtocolError(Exception):

    def __init__(self, detail: str, returncode: int = -1):
        self.returncode: int = returncode
        detail = detail.strip()
        super().__init__(detail)


class RpcSetupError(Exception):

    def __init__(self, detail: str, returncode: int = -1):
        self.returncode: int = returncode
        detail = detail.strip()
        super().__init__(detail)
