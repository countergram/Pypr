import sublime
import subprocess

PATH = None


def env():
    " Return an environment to pass to subprocess "
    global PATH
    if sublime.platform() == 'osx' and PATH is None:
        PATH = osx_path()

    return {"PATH": PATH} if PATH else None


def osx_path():
    " Compenate for ST3 not using the shell's PATH unless opened from cli "
    # https://github.com/int3h/SublimeFixMacPath/blob/master/FixPath.py
    command = "/usr/bin/login -fpql $USER $SHELL -l -c 'echo -n $PATH'"
    return subprocess.check_output(command, shell=True).decode('utf8')
