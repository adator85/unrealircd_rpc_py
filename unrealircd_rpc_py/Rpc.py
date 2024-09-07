from typing import Union
from dataclasses import dataclass
from unrealircd_rpc_py.Connection import Connection

class Rpc:

    @dataclass
    class ModelRpcInfo:
        name: str
        module: str
        version: str

    DB_RPC_INFO: list[ModelRpcInfo] = []


    def __init__(self, Connection: Connection) -> None:

        # Record the original response
        self.original_response: str = ''

        # Get the Connection instance
        self.Connection = Connection
        self.Logs = Connection.Logs
        self.Error = Connection.Error

    def info(self) -> Union[list[ModelRpcInfo], None, bool]:
        """A response object, with in the result object a "methods" object which is a list of: the API method with in that the name, module name and module version.

        Returns:
            Union[list[ModelRpcInfo], None, bool]: List of ModelRpcInfo, None if nothing or False if error
        """
        try:
            response = self.Connection.query(method='rpc.info')
            self.original_response = response

            if response is None:
                return False

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.set_error(response)
                return False

            rpcinfos = response['result']['methods']

            for rpcinfo in rpcinfos:
                self.DB_RPC_INFO.append(
                        self.ModelRpcInfo(
                            name=rpcinfos[rpcinfo]['name'],
                            module=rpcinfos[rpcinfo]['module'],
                            version=rpcinfos[rpcinfo]['version'],
                            )
                )

            return self.DB_RPC_INFO

        except KeyError as ke:
            self.Logs.error(ke)
        except Exception as err:
            self.Logs.error(err)

    def set_issuer(self, name: str) -> bool:
        """Set who is the issuer of all the subsequent commands that are done. 

        This information will be used by the logging system and communicate to servers and IRCOps in the unrealircd.org/issued-by message tag.

        This method only exists in UnrealIRCd 6.1.0 and later

        Args:
            name (str): the name of the person who is issuing the commands, eg. the current logged in person to the admin panel. Note: This name must conform to the regular nickname rules, eg. may not contain spaces and the like.

        Returns:
            bool: True if success
        """
        response = self.Connection.query(
            method='rpc.set_issuer', 
            param={"name": name}
            )

        self.original_response = response

        if response is None:
            return False

        if 'error' in response:
            self.Connection.set_error(response)
            return False

        if 'result' in response:
            if response['result']:
                self.Logs.debug(response)
                return True

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
        response = self.Connection.query(
            method='rpc.add_timer',
            param={"timer_id": timer_id, "every_msec": every_msec, "request": request}
            )

        self.original_response = response

        if response is None:
            return False

        if 'error' in response:
            self.Connection.set_error(response)
            return False

        if 'result' in response:
            if response['result']:
                self.Logs.debug(response)
                return True

        return True

    def del_timer(self, timer_id: str) -> bool:
        """Remove a previously added timer. Note that you can only cancel timers that belong to your own connection.

        This method only exists in UnrealIRCd 6.1.0 and later

        Args:
            timer_id (str): the name/id of the timer that needs to be canceled.

        Returns:
            bool: True if success
        """
        response = self.Connection.query(
            method='rpc.del_timer', 
            param={"timer_id": timer_id}
            )

        self.original_response = response

        if response is None:
            return False

        if 'error' in response:
            self.Connection.set_error(response)
            return False

        if 'result' in response:
            if response['result']:
                self.Logs.debug(response)
                return True

        return True
