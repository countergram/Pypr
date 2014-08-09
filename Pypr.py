import sublime
import subprocess
from .commands import open_module, open_module_py2


PATH = None


def plugin_loaded():
    if sublime.platform() == 'osx':
        fix_path()


def fix_path():
    " Compenate for ST3 not using the shell's PATH unless opened from cli "
    # https://github.com/int3h/SublimeFixMacPath/blob/master/FixPath.py
    global PATH
    command = "/usr/bin/login -fpql $USER $SHELL -l -c 'echo -n $PATH'"
    PATH = subprocess.check_output(command, shell=True).decode('utf8')


def env():
    " Return an environment to pass to subprocess "
    return {"PATH": PATH} if PATH else None
