from types import SimpleNamespace
from typing import Union
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as Dfn

class Stats:

    def __init__(self, connection: Connection) -> None:

        # Store the original response
        self.response_raw: str
        """Original response used to see available keys."""

        self.response_np: SimpleNamespace
        """Parsed JSON response providing access to all keys as attributes."""

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs
        self.Error = connection.Error

    @property
    def get_error(self) -> Dfn.RPCError:
        return self.Error

    def get(self, object_detail_level:int = 1) -> Union[Dfn.Stats, None]:
        """Get some quick basic statistics.

        Args:
            object_detail_level (int, optional): set the detail of the response object. The user.countries will be included from level 1+. The default object_detail_level is 1. Defaults to 1.

        Returns:
            list[ModelStats]: The Stats model or None if there is an error see Error Property
        """
        try:
            self.Connection.EngineError.init_error()

            response: dict[str, dict] = self.Connection.query('stats.get', param={'object_detail_level': object_detail_level})

            self.response_raw = response
            self.response_np = self.Connection.json_response_np

            if response is None:
                self.Logs.error('Empty response')
                self.Connection.EngineError.set_error(code=-2, message='Empty response')
                return None

            if 'error' in response:
                self.Logs.error(response['error']['message'])
                self.Connection.EngineError.set_error(**response["error"])
                return None

            result: dict = response.get('result', {})
            
            server_obj = Dfn.StatsServer(**result.get('server', Dfn.StatsServer().to_dict()))
            channel_obj = Dfn.StatsChannel(**result.get('channel', Dfn.StatsChannel().to_dict()))
            server_ban_obj = Dfn.StatsServerBan(**result.get('server_ban', Dfn.StatsServerBan().to_dict()))
            
            user_dict: dict[str, dict] = result.get('user', {})

            # list of stats user counrties
            user_country_list_obj: list[Dfn.StatsUserCountries] = []
            user_countries_list: list[dict] = user_dict.get('countries', [])
            for user_country in user_countries_list:
                user_country_list_obj.append(Dfn.StatsUserCountries(**user_country))

            if 'countries' in user_dict:
                user_dict.pop('countries')

            user_obj = Dfn.StatsUser(**user_dict, countries=user_country_list_obj)

            statsObject = Dfn.Stats(
                server=server_obj,
                user=user_obj,
                channel=channel_obj,
                server_ban=server_ban_obj
            )

            return statsObject

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return None
