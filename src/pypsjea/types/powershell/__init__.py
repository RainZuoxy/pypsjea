import atexit

from pypsrp.client import Client
from pypsrp.exceptions import WinRMError, WinRMTransportError, AuthenticationError
from pypsrp.powershell import RunspacePool, PowerShell, PSDataStreams

from pypsjea.consts import TransportType
from pypsjea.types import CommandItem
from pypsjea.exception import AuthorizationFailure, AuthenticationFailure
from pypsjea.logger import get_logger
from pypsjea.util import get_int_env


class BasePowerShell:
    """
    Execute PowerShell command
    """
    _logger = get_logger(__name__)
    POWERSHELL_READ_TIMEOUT = get_int_env('POWERSHELL_READ_TIMEOUT', 30)
    POWERSHELL_OPERATION_TIMEOUT = get_int_env('POWERSHELL_OPERATION_TIMEOUT', 20)
    POWERSHELL_CONNECTION_TIMEOUT = get_int_env('POWERSHELL_CONNECTION_TIMEOUT', 30)

    def __init__(self, hostname, username, password, port=None, transport=TransportType.NEGOTIATE.value, ssl=False):
        self.client = Client(
            hostname, port=port, username=username, password=password, ssl=ssl, auth=transport,
            read_timeout=self.POWERSHELL_READ_TIMEOUT, operation_timeout=self.POWERSHELL_OPERATION_TIMEOUT,
            connection_timeout=self.POWERSHELL_CONNECTION_TIMEOUT)

        atexit.register(self.close)

    def close(self):
        """
        Close the wsman connection if needed
        :return:
        """
        self.client.close()
        self._logger.debug("Closing connection")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_client(self) -> Client:
        """
        If you want to use the function(self.get_client().execute_ps(script=script)),
        you will ensure that "Out-String","Invoke-Expression" can be used.
        :return: Return "Client" object. And you can use client.execute_ps to input script.
        But it is not a raw script, it uses "Invoke-Expression" to parser "script".
        So when you want to use it, you will confirm that you can use "Invoke-Expression"
        when you are not under default configuration_name.
        """
        return self.client

    def execute_script(self, script: str) -> tuple[list, PSDataStreams, bool]:
        """
        This function do not use under JEA.
        When your configuration_name is not "Microsoft.PowerShell"(default),it will raise error:
        The syntax is not supported by this runspace. This can occur if the runspace is
        in no-language mode."
        :param script: e.g.['script1','script2','script3',...];And this is like script1; script2; script3;...
        :return: "PowerShell".output,PSDataStreams,bool.
        output: It is a list, if Powershell.had_errors is True, it is a empty list. Else you can
        operate it after returning through '\n'.join(list) to convert to str.
        """
        try:
            with RunspacePool(self.client.wsman) as pool:
                ps = PowerShell(pool)
                ps.add_script(script)
                ps.invoke()
                return ps.output, ps.streams, ps.had_errors
        except WinRMTransportError as error:
            raise AuthorizationFailure(error.message)
        except AuthenticationError as error:
            raise AuthenticationFailure(error.args[0])
        except Exception as error:
            raise Exception(f"Unexpected error happens on powershell command - {error}")

    def execute_cmd(
            self,
            cmds: list[CommandItem],
    ) -> tuple[list, PSDataStreams, bool]:
        """
        This function is use add_cmdlet,add_parameters just in no JEA
        :param cmds: cmd set e.g.[
            CommandItem(cmdlet='Get-ComputerInfo'),
            CommandItem(cmdlet='Select-Object',parameters={'Property','Column'}),
            ...
            ]
        And this is like Get-ComputerInfo | Select-Object -Property Column | ...
        :return: "Powershell".output,PSDataStreams,bool.
        output:It is a list, if Powershell.had_errors is True, it is a empty list. Else you can
        operate it after returning through '\n'.join(list) to convert to str.
        """
        try:
            with RunspacePool(self.client.wsman) as pool:
                ps = PowerShell(pool)
                for cmd in cmds:
                    ps.add_cmdlet(cmd.cmdlet)
                    if cmd.parameters:
                        ps.add_parameters(cmd.parameters)
                ps.invoke()
                return ps.output, ps.streams, ps.had_errors
        except WinRMTransportError as error:
            raise AuthorizationFailure(error.message)
        except AuthenticationError as error:
            raise AuthenticationFailure(error.args[0])
        except Exception:
            raise Exception("Unexpected error happens on powershell command")
          
    def execute_jea_cmd(
            self,
            cmds: list[CommandItem],
            jea_endpoint: str,
    ) -> tuple[list, PSDataStreams, bool]:
        """
        This function is use add_cmdlet,add_parameters in JEA
        :param cmds: cmd set e.g.[
            CommandItem(cmdlet='Get-ComputerInfo'),
            CommandItem(cmdlet='Select-Object',parameters={'Property','Column'}),
            ...
            ]
        And this is like Get-ComputerInfo | Select-Object -Property Column | ...
        :param jea_endpoint: JEA configuration name
        :return: "Powershell".output,PSDataStreams,bool.
        output:It is a list, if Powershell.had_errors is True, it is a empty list. Else you can
        operate it after returning through '\n'.join(list) to convert to str.
        """
        try:
            with RunspacePool(self.client.wsman, configuration_name=jea_endpoint) as pool:
                ps = PowerShell(pool)
                for cmd in cmds:
                    ps.add_cmdlet(cmd.cmdlet)
                    if cmd.parameters:
                        ps.add_parameters(cmd.parameters)
                ps.invoke()
                return ps.output, ps.streams, ps.had_errors
        except WinRMTransportError as error:
            raise AuthorizationFailure(error.message)
        except AuthenticationError as error:
            raise AuthenticationFailure(error.args[0])
        except Exception:
            raise Exception("Unexpected error happens on powershell command")
          
    def handle_powershell_error(self, powershell: PowerShell, message: str):
        if not powershell.had_errors:
            return
        errors = powershell.streams.error
        error = "\n".join([str(err) for err in errors])
        raise WinRMError(f"{message}: {error}")
