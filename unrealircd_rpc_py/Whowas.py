from types import SimpleNamespace
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as dfn

class Whowas:

    DB_WHOWAS: list[dfn.Whowas] = []

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

    def get(self, nick: str = None, ip: str = None, object_detail_level:int = 2) -> list[dfn.Whowas]:
        """Get WHOWAS history of a user. 6.1.0+

        Args:
            nick (str, optional): The nick name to search for. Defaults to None.
            ip (str, optional): The IP address to search for. Defaults to None.
            object_detail_level (int, optional): set the detail of the response object, this is similar to the Detail level column in Structure of a client object. In this RPC call it defaults to 2 if this parameter is not specified. Defaults to 2.

        Returns:
            List[dfn.Whowas]: The Whowas model or Empty Whowas model
        """
        try:
            self.DB_WHOWAS = []
            self.Connection.EngineError.init_error()

            response = self.Connection.query('whowas.get', param={'nick': nick, 'ip': ip, 'object_detail_level': object_detail_level})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return self.DB_WHOWAS

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return self.DB_WHOWAS

            whowass: list[dict] = response["result"]["list"]

            for whowas in whowass:

                whowas_exclude_user = whowas.copy()
                whowas_exclude_user.pop('user', None)

                self.DB_WHOWAS.append(
                    dfn.Whowas(
                        **whowas_exclude_user,
                        user=dfn.WhowasUser(**whowas.get('user', {}))
                    )
                )

            return self.DB_WHOWAS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
        except Exception as err:
            self.Logs.error(f'General error: {err}')
