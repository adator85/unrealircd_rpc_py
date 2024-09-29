from types import SimpleNamespace
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as dfn

class Rpc:

    DB_RPC_INFO: list[dfn.RpcInfo] = []

    def __init__(self, Connection: Connection) -> None:

        # Store the original response
        self.response_raw: str
        """Original response used to see available keys."""

        self.response_np: SimpleNamespace
        """Parsed JSON response providing access to all keys as attributes."""

        # Get the Connection instance
        self.Connection = Connection
        self.Logs = Connection.Logs
        self.Error = Connection.Error

    def info(self) -> list[dfn.RpcInfo]:
        """A response object, with in the result object a "methods" object which is a list of: the API method with in that the name, module name and module version.

        Returns:
            list[RpcInfo]: List of RpcInfo, empty object if error
        """
        try:
            self.DB_RPC_INFO = []
            self.Connection.EngineError.init_error()

            response = self.Connection.query(method='rpc.info')

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return self.DB_RPC_INFO

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return self.DB_RPC_INFO

            rpcinfos: dict[dict, dict] = response['result']['methods']

            for rpcinfo in rpcinfos:
                self.DB_RPC_INFO.append(
                        dfn.RpcInfo(**rpcinfos.get(rpcinfo, {}))
                )

            return self.DB_RPC_INFO

        except KeyError as ke:
            self.Logs.error(ke)
            return self.DB_RPC_INFO
        except Exception as err:
            self.Logs.error(err)
            return self.DB_RPC_INFO

    def set_issuer(self, name: str) -> bool:
        """Set who is the issuer of all the subsequent commands that are done. 

        This information will be used by the logging system and communicate to servers and IRCOps in the unrealircd.org/issued-by message tag.

        This method only exists in UnrealIRCd 6.1.0 and later

        Args:
            name (str): the name of the person who is issuing the commands, eg. the current logged in person to the admin panel. Note: This name must conform to the regular nickname rules, eg. may not contain spaces and the like.

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(
                method='rpc.set_issuer', 
                param={"name": name}
                )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            if 'result' in response:
                if response['result']:
                    self.Logs.debug(response)
                    return True

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return True
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return True

    def add_timer(self, timer_id: str, every_msec: int, request: dict) -> bool:
        """Add a timer so a JSON-RPC request is executed at certain intervals.

        This method only exists in UnrealIRCd 6.1.0 and later

        exemple of request:

        {"jsonrpc": "2.0", "method": "stats.get", "params": {}, "id": 555}

        Args:
            timer_id (str): the name/id of the timer, this so you can cancel it via rpc.del_timer later. It must be unique for this RPC connection.
            every_msec (int): the timer will be executed every -this- milliseconds. The minimum value is 250 (a quarter of a second).
            request (dict): the full JSON-RPC request, so {"jsonrpc":"2.0" etc. etc.

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(
                method='rpc.add_timer',
                param={"timer_id": timer_id, "every_msec": every_msec, "request": request}
                )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            if 'result' in response:
                if response['result']:
                    self.Logs.debug(response)
                    return True

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')

    def del_timer(self, timer_id: str) -> bool:
        """Remove a previously added timer. Note that you can only cancel timers that belong to your own connection.

        This method only exists in UnrealIRCd 6.1.0 and later

        Args:
            timer_id (str): the name/id of the timer that needs to be canceled.

        Returns:
            bool: True if success
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(
                method='rpc.del_timer', 
                param={"timer_id": timer_id}
                )

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            if 'result' in response:
                if response['result']:
                    self.Logs.debug(response)
                    return True

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')
