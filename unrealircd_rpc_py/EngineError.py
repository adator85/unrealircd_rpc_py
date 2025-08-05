from unrealircd_rpc_py.Definition import RPCError

class EngineError:

    """Engine Error: This attribut will contain the current Error"""

    def __init__(self):
        self.Error = RPCError()
        """Engine Error: This attribut will contain the current Error"""

    def init_error(self):

        self.Error.code = 0
        self.Error.message = None

    def set_error(self, code:int, message:str):
        """Engine Error set the error

        ### Error Code:
        These are possible Internal Errors:
        ```
        -1: Connection Error
        -2: Empty response
        -3: Exception Error
        ```

        Args:
            code (int): the error code
            message (str): the message of the error
        """
        self.Error.code = code
        self.Error.message = message
