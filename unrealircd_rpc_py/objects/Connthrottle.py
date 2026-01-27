from typing import TYPE_CHECKING
import unrealircd_rpc_py.objects.Definition as Dfn
from unrealircd_rpc_py.utils import utils

if TYPE_CHECKING:
    from unrealircd_rpc_py.connections.sync.IConnection import IConnection


class ConnThrottle:

    def __init__(self, connection: 'IConnection') -> None:

        # Get the Connection instance
        self.Connection = connection
        self.Logs = connection.Logs

    def status(self) -> Dfn.ConnThrottle:
        """The status of connection throttle

        Returns:
            ConnThrottle: The ConnThrottle object
        """
        try:
            response: dict[str, dict] = self.Connection.query('connthrottle.status')
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return  Dfn.ConnThrottle(error=response_model.error)

            _status: dict = response_model.result
            _counters = _status.pop('counters')
            _stats_last_minute = _status.pop('stats_last_minute')
            _config = _status.pop('config')

            connthrottle = Dfn.ConnThrottle(**_status,
                                               counters=Dfn.CTCounters(**_counters),
                                               stats_last_minute=Dfn.CTStatsLastMinute(**_stats_last_minute),
                                               config=Dfn.CTConfig(**_config)
            )

            return connthrottle

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.ConnThrottle(error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.ConnThrottle(error=Dfn.RPCErrorModel(-1, err))

    def set(self, enabled: bool) -> Dfn.RPCResult:
        """Activate or Deactivate the Connthrottle module

        Args:
            enabled (bool): True if your want to enable the module.
                otherwise False.
        Returns:
            RPCResult: The Standard response if success or error
        """
        try:
            response: dict[str, dict] = self.Connection.query(
                'connthrottle.set', {'enabled': enabled})
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.RPCResult(error=response_model.error)

            return response_model

        except KeyError as ke:
            self.Logs.error(f'KeyError: {ke}')
            return Dfn.RPCResult(
                error=Dfn.RPCErrorModel(-1, ke.__str__()))
        except Exception as err:
            self.Logs.error(f'General error: {err}')
            return Dfn.RPCResult(
                error=Dfn.RPCErrorModel(-1, err.__str__()))

    def reset(self) -> Dfn.RPCResult:
        """Reset the Connthrottle module

        Returns:
            RPCResult: The standard RPC Result.
        """
        try:
            response: dict[str, dict] = self.Connection.query('connthrottle.reset')
            response_model = utils.construct_rpc_response(response)

            if response_model.error.code != 0:
                self.Logs.error(f"Code: {response_model.error.code} "
                                f"- Msg: {response_model.error.message}")
                return Dfn.RPCResult(error=response_model.error)

            return response_model

        except Exception as err:
            self.Logs.error(f'General Error: {err}')
            return Dfn.RPCResult(
                error=Dfn.RPCErrorModel(-1, err.__str__())
            )
