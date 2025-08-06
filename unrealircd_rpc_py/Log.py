from types import SimpleNamespace
from typing import Union, Literal, Optional
from time import time
from unrealircd_rpc_py.Connection import Connection
from unrealircd_rpc_py.Definition import RPCError


class Log:

    def __init__(self, connection: Connection) -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs
        self.Error = connection.Error

    @property
    def get_error(self) -> RPCError:
        return self.Error

    @property
    def get_response(self) -> Union[dict, None]:
        return self.Connection.get_response()

    @property
    def get_response_np(self) -> Union[SimpleNamespace, None]:
        return self.Connection.get_response_np()

    def list_(self, sources: Optional[list] = None) -> Union[SimpleNamespace, None]:
        """Fetch past log entries (since boot).

        Returns:
            list[ModelNameBan]: List of ModelNameBan, None if nothing or Error see the property
        """
        try:
            self.Connection.EngineError.init_error()

            response: dict[str, dict] = self.Connection.query(
                method='log.list', 
                param={"sources": sources}
                )

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return None

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return None

            return self.get_response_np

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return None

    def send(self, msg: str, level: Literal['debug','info','warn','error','fatal'],
             subsystem: str, event_id: str, timestamp: float = time()
             ) -> bool:
        """ Send a log message / server notice.

        Requires UnrealIRCd 6.1.8 or later

        Args:
            msg (str): The message you want to send to the server
            level (Literal[&#39;debug&#39;,&#39;info&#39;,&#39;warn&#39;,&#39;error&#39;,&#39;fatal&#39;]): You can pick the level in the list
            subsystem (str): You can put anything you want as a subsystem
            event_id (str): You can put anything you want as a event_id
            timestamp (float, optional): The current timestamp. Defaults to time().

        Returns:
            bool: True if is okey, else if there is an error
        """
        # waiting for the documentation.
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query(
                    method='log.send',
                    param={"msg": msg, "level": level, "subsystem": subsystem, "event_id": event_id, "timestamp": timestamp}
                    )

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return False

            self.Logs.debug(response)

            return True

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return False
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return False