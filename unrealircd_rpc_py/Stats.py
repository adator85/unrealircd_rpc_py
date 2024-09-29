from types import SimpleNamespace
from typing import Union
from unrealircd_rpc_py.Connection import Connection
import unrealircd_rpc_py.Definition as dfn

class Stats:

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

    def get(self, object_detail_level:int = 1) -> Union[dfn.Stats, None]:
        """Get some quick basic statistics.

        Args:
            object_detail_level (int, optional): set the detail of the response object. The user.countries will be included from level 1+. The default object_detail_level is 1. Defaults to 1.

        Returns:
            list[ModelStats]: The Stats model or None if there is an error see Error Property
        """
        try:
            self.Connection.EngineError.init_error()

            response = self.Connection.query('stats.get', param={'object_detail_level': object_detail_level})

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

            stats: dict = response['result']
            stats_user_copy: dict = stats.get('user', {}).copy()
            stats_user_copy.pop('countries')

            stats_user_country_copy: list[dict] = stats.get('user', {}).get('countries', []).copy()

            StatsUserObj = dfn.StatsUser(
                **stats_user_copy,
                countries=[dfn.StatsUserCountries(**country) for country in stats_user_country_copy]
            )

            statsObject = dfn.Stats(
                server=dfn.StatsServer(**stats.get('server', {})),
                user=StatsUserObj,
                channel=dfn.StatsChannel(**stats.get('channel', {})),
                server_ban=dfn.StatsServerBan(**stats.get('server_ban', {}))
            )

            return statsObject

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return None
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return None
