from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class Stats:

    def __init__(self, connection: 'IConnection') -> None:
        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def get(self, object_detail_level: int = 1) -> Dfn.Stats:
        """Get some quick basic statistics.
        {"jsonrpc": "2.0", "method": "stats.get", "params": {}, "id": 123}
        Args:
            object_detail_level (int, optional):
                set the detail of the response object.
                The user.countries will be included from level 1+.
                The default object_detail_level is 1. Defaults to 1.

        Returns:
            Stats: The Stats model.
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'stats.get',
                param={'object_detail_level': object_detail_level})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.Stats(error=response_model.error)

            result: dict = response.get('result', {})
            server_obj = Dfn.StatsServer(
                **result.pop('server', Dfn.StatsServer().to_dict())
            )
            channel_obj = Dfn.StatsChannel(
                **result.pop('channel', Dfn.StatsChannel().to_dict())
            )
            server_ban_obj = Dfn.StatsServerBan(
                **result.pop('server_ban', Dfn.StatsServerBan().to_dict())
            )
            user_dict: dict[str, dict] = result.get('user', {})

            # list of stats user counrties
            user_country_list_obj: list[Dfn.StatsUserCountries] = []
            user_countries_list: list[dict] = user_dict.pop('countries', [])
            for user_country in user_countries_list:
                user_country_list_obj.append(
                    Dfn.StatsUserCountries(**user_country)
                )

            user_obj = Dfn.StatsUser(
                **user_dict, countries=user_country_list_obj)

            stats_obj = Dfn.Stats(
                server=server_obj,
                user=user_obj,
                channel=channel_obj,
                server_ban=server_ban_obj
            )

            return stats_obj

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.Stats(
                error=Dfn.RPCErrorModel(code=-1, message=ke.__str__())
            )
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.Stats(
                error=Dfn.RPCErrorModel(code=-1, message=err.__str__())
            )
