from .native.ping import ping
from .native.clone import clone
from .native.venv import venv

CMD_FUNCS = {
    'native': {
        'ping': ping,
        'clone': clone,
        'venv': venv
    }
}



