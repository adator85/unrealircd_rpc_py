"""
Log object for UnrealIRCd JSON-RPC
Minimum Unrealircd version: 6.1.8
"""
import unrealircd_rpc_py.objects.Definition as Dfn
from types import SimpleNamespace
from typing import Union, Literal, Optional, TYPE_CHECKING
from time import time
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class Log:

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def list_(self, sources: Optional[list] = None
              ) -> Union[SimpleNamespace, Dfn.RPCResult]:
        """Fetch past log entries (since boot).

        Returns:
            list[ModelNameBan]: List of ModelNameBan,
                None if nothing or Error see the property
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                method='log.list',
                param={"sources": sources}
                )

            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return utils.dict_to_namespace(response)

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))

    def send(self, msg: str,
             level: Literal['debug', 'info', 'warn', 'error', 'fatal'],
             subsystem: str, event_id: str, timestamp: float = time()
             ) -> Dfn.RPCResult:
        """ Send a log message / server notice.

        Requires UnrealIRCd 6.1.8 or later

        Args:
            msg (str): The message you want to send to the server
            level (str): You can pick the level in the list
            subsystem (str): You can put anything you want as a subsystem
            event_id (str): You can put anything you want as a event_id
            timestamp (float, optional): The current timestamp.
                Defaults to time().

        Returns:
            bool: True if is okey, else if there is an error
        """
        # waiting for the documentation.
        try:
            response = self.Connection.query(
                    method='log.send',
                    param={"msg": msg, "level": level, "subsystem": subsystem,
                           "event_id": event_id, "timestamp": timestamp}
                    )

            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return response_model

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))
