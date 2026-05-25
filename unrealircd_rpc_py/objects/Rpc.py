from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class Rpc:

    DB_RPC_INFO: list[Dfn.RpcInfo] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def info(self) -> list[Dfn.RpcInfo]:
        """A response object, with in the result object a "methods" object
        which is a list of: the API method with in that the name,
        module name and module version.

        Returns:
            list[RpcInfo]: List of RpcInfo
        """
        try:
            self.DB_RPC_INFO: list[Dfn.RpcInfo] = []
            response: dict[str, dict] = self.Connection.query('rpc.info')
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                self.DB_RPC_INFO.append(
                    Dfn.RpcInfo(error=response_model.error)
                )
                return self.DB_RPC_INFO

            rpcinfos: dict[dict, dict] = response_model.result.get(
                'methods', {}
            )

            for rpcinfo in rpcinfos:
                self.DB_RPC_INFO.append(
                        Dfn.RpcInfo(**rpcinfos.get(rpcinfo, {}))
                )

            return self.DB_RPC_INFO

        except KeyError as ke:
            self.Logs.error(ke)
            return []
        except Exception as err:
            self.Logs.error(err)
            return []

    def set_issuer(self, name: str) -> Dfn.RPCResult:
        """Set who is the issuer of all the subsequent commands that are done.

        This information will be used by the logging system and communicate
        to servers and IRCOps in the unrealircd.org/issued-by message tag.

        This method only exists in UnrealIRCd 6.1.0 and later

        Args:
            name (str): the name of the person who is issuing the commands,
                eg. the current logged in person to the admin panel.
                Note: This name must conform to the regular nickname rules,
                eg. may not contain spaces and the like.

        Returns:
            RPCResult: The RPC Result object
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='rpc.set_issuer',
                param={"name": name}
                )

            response_model = utils.construct_rpc_response(response)

            if response_model.error.code == 0:
                self.Logs.debug(
                    f"Method: {response_model.method} - Result: Success"
                )
                return response_model
            else:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(
                result=False, error=Dfn.RPCErrorModel(-1, ke.__str__())
            )
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(
                result=False, error=Dfn.RPCErrorModel(-1, err.__str__())
            )

    def add_timer(self, timer_id: str, every_msec: int, request: dict
                  ) -> Dfn.RPCResult:
        """Add a timer so a JSON-RPC request is executed at certain
        intervals.

        This method only exists in UnrealIRCd 6.1.0 and later

        exemple of request:

        {"jsonrpc": "2.0",
        "method": "rpc.add_timer",
        "params": {"timer_id":"test","every_msec":1000,
                    "request":{"jsonrpc": "2.0",
                               "method": "stats.get",
                               "params": {}, "id": 555}},
                               "id": 123}

        Args:
            timer_id (str): the name/id of the timer, this so you can cancel
                it via rpc.del_timer later. It must be unique for this RPC
                connection.
            every_msec (int): the timer will be executed every -this-
                milliseconds. The minimum value is 250
                (a quarter of a second).
            request (dict): the full JSON-RPC request, so
                {"jsonrpc":"2.0" etc. etc.

        Returns:
            RPCResult: The RPC Result object
        """
        try:

            response: dict[str, dict] = self.Connection.query(
                method='rpc.add_timer',
                param={"timer_id": timer_id, "every_msec": every_msec,
                       "request": request}
                )

            response_model = utils.construct_rpc_response(response)

            if response_model.error.code == 0:
                self.Logs.debug(
                    f"Method: {response_model.method} - Result: Success"
                )
                return response_model
            else:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(
                result=False, error=Dfn.RPCErrorModel(-1, ke.__str__())
            )
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(
                result=False, error=Dfn.RPCErrorModel(-1, err.__str__())
            )

    def del_timer(self, timer_id: str) -> Dfn.RPCResult:
        """Remove a previously added timer. Note that you can only cancel
        timers that belong to your own connection.

        This method only exists in UnrealIRCd 6.1.0 and later

        Args:
            timer_id (str): the name/id of the timer that needs to be
                canceled.

        Returns:
            RPCResult: The RPC Result object
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='rpc.del_timer',
                param={"timer_id": timer_id}
                )

            response_model = utils.construct_rpc_response(response)

            if response_model.error.code == 0:
                self.Logs.debug(
                    f"Method: {response_model.method} - Result: Success"
                )
                return response_model
            else:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(
                result=False, error=Dfn.RPCErrorModel(-1, ke.__str__())
            )
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(
                result=False, error=Dfn.RPCErrorModel(-1, err.__str__())
            )
