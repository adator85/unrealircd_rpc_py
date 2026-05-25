from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class Whowas:

    DB_WHOWAS: list[Dfn.Whowas] = []

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def get(self, nick: str = None, ip: str = None,
            object_detail_level: int = 2) -> list[Dfn.Whowas]:
        """Get WHOWAS history of a user. 6.1.0+

        Args:
            nick (str, optional): The nick name to search for.
            Defaults to None.

            ip (str, optional): The IP address to search for.
            Defaults to None.

            object_detail_level (int, optional): set the detail
            of the response object, this is similar to the
            Detail level column in Structure of a client object.
            In this RPC call it defaults to 2 if this parameter is not
            specified. Defaults to 2.

        Returns:
            List[dfn.Whowas]: The Whowas model or Empty Whowas model
        """
        try:
            self.DB_WHOWAS = []
            response: dict[str, dict] = self.Connection.query(
                'whowas.get',
                param={'nick': nick,
                       'ip': ip,
                       'object_detail_level': object_detail_level}
            )
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} - "
                                f"Msg: {response_model.error.message}")
                return response_model

            whowass: list[dict] = (response_model.result
                                   .get('result', {})
                                   .get('list', []))

            for whowas in whowass:
                whowas_exclude_objs = whowas.copy()
                whowas_exclude_objs.pop('user', None)
                whowas_exclude_objs.pop('geoip', None)

                self.DB_WHOWAS.append(
                    Dfn.Whowas(
                        **whowas_exclude_objs,
                        user=Dfn.WhowasUser(**whowas.get(
                            'user',
                            Dfn.WhowasUser().to_dict())
                                            ),
                        geoip=Dfn.Geoip(**whowas.get('geoip',
                                                     Dfn.Geoip().to_dict()))
                    )
                )

            if not whowass:
                self.DB_WHOWAS.append(
                    Dfn.Whowas(
                        error=Dfn.RPCErrorModel(
                            -1,
                            "Empty response from whowas.get")
                    )
                )

            return self.DB_WHOWAS

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(error=Dfn.RPCErrorModel(-1, err.__str__()))
