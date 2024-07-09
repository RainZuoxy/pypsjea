import os

def get_int_env(env, default=None):
    """
    Get an integer environment variable by its name
    :param env: Environment variable name
    :param default: Default value if env not exists or not a valid integer
    :return: int value of the env or the default
    """
    _value = os.environ.get(env)
    try:
        _value = int(_value)
    except Exception:
        _value = default
    return _value
