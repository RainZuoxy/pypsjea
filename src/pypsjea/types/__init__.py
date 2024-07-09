from dataclasses import dataclass


@dataclass
class CommandItem:
    """
    When you use PowerShellCollector.execute_cmd, you will use this object to structure param:cmds
    """
    cmdlet: str
    parameters: dict = None

    def _parse(self):
        parameters = ''
        if self.parameters:
            for k, v in self.parameters.items():
                parameters = f"{parameters} -{k}{f' {v}' if v else ''}"

        return f"{self.cmdlet}{parameters}"

    def __str__(self):
        return self._parse()

    def __repr__(self):
        return f"<PowerShell Command: {self._parse()}>"

