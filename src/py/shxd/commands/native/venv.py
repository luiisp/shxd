import requests
import base64
import itertools
import re
import sys
import subprocess
import os
import platform
import venv as venv_module
from ...utils import Colors

def is_virtual_environment():
    return (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix) or 
        os.environ.get('VIRTUAL_ENV') is not None
    )


def venv():
    if is_virtual_environment():
        venv_path = os.environ.get('VIRTUAL_ENV')
        system = platform.system()
        sys.stdout.write(f'\n{Colors().green} ✅ ({venv_path}) You are in a virtual environment.{Colors().reset}\n')
        sys.stdout.write(f'\n{Colors().yellow} ⚠️ Do you want to proceed and deactivate the virtual environment? {Colors().reset} (Y/N): ')
        sys.stdout.flush()
        entry = sys.stdin.readline().strip()  
        if entry.lower() == 'y':
            sys.stdout.write(f'\n{Colors().green} ✅ Deactivating the virtual environment...{Colors().reset}\n')
            os.environ.pop('VIRTUAL_ENV')
            sys.prefix = sys.base_prefix

            return True
        return False
    else:
        sys.stdout.write(f'\n{Colors().yellow} ⚠️ You are not in virtual environment {Colors().reset}\n')
        sys.stdout.write(f'\n{Colors().yellow}  {Colors().reset} (Y/N): ')
        return False