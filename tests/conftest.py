import sys
import types


if "dotenv" not in sys.modules:
    dotenv_module = types.ModuleType("dotenv")
    dotenv_module.load_dotenv = lambda *args, **kwargs: None
    sys.modules["dotenv"] = dotenv_module


if "mysql" not in sys.modules:
    mysql_module = types.ModuleType("mysql")
    connector_module = types.ModuleType("mysql.connector")

    def _unsupported_connect(*args, **kwargs):
        raise RuntimeError(
            "mysql.connector.connect is unavailable in unit tests"
        )

    connector_module.connect = _unsupported_connect
    mysql_module.connector = connector_module

    sys.modules["mysql"] = mysql_module
    sys.modules["mysql.connector"] = connector_module
