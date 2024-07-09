class AuthenticationFailure(Exception):
    """Authentication error (username/password, SSH key etc)"""
    pass


class AuthorizationFailure(Exception):
    """Authorization error or permission denied"""
    pass
