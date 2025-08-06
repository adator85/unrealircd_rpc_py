from types import SimpleNamespace
from typing import Union
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as Dfn

class Whowas:

    DB_WHOWAS: list[Dfn.Whowas] = []

    def __init__(self, connection: Connection) -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs
        self.Error = connection.Error

    @property
    def get_error(self) -> Dfn.RPCError:
        return self.Error

    @property
    def get_response(self) -> Union[dict, None]:
        return self.Connection.get_response()

    @property
    def get_response_np(self) -> Union[SimpleNamespace, None]:
        return self.Connection.get_response_np()

    def get(self, nick:str = None, ip:str = None, object_detail_level:int = 2) -> list[Dfn.Whowas]:
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

            response: dict[str, dict] = self.Connection.query('whowas.get', param={'nick': nick, 'ip': ip, 'object_detail_level': object_detail_level})

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return self.DB_WHOWAS

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return self.DB_WHOWAS

            whowass: list[dict] = response.get('result', {}).get('list', []) # ["result"]["list"]

            for whowas in whowass:

                whowas_exclude_objs = whowas.copy()
                whowas_exclude_objs.pop('user', None)
                whowas_exclude_objs.pop('geoip', None)

                self.DB_WHOWAS.append(
                    Dfn.Whowas(
                        **whowas_exclude_objs,
                        user=Dfn.WhowasUser(**whowas.get('user', Dfn.WhowasUser().to_dict())),
                        geoip=Dfn.Geoip(**whowas.get('geoip', Dfn.Geoip().to_dict()))
                    )
                )

            return self.DB_WHOWAS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return []
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return []
