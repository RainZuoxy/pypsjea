from enum import Enum

class TransportType(Enum):
    NEGOTIATE = 'negotiate'
    CREDSSP = 'credssp'
    KERBEROS = 'kerberos'
    NTLM = 'ntlm'
