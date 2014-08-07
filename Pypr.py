import sublime
import sublime_plugin

import os.path
import imp
import subprocess
import re

non_alphanum = re.compile(r"[^a-zA-Z0-9.]")
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


class open_module(sublime_plugin.WindowCommand):

    " Prompt for a package name and attempt to load the file or dir "

    py2 = False

    def run(self):
        self.window.show_input_panel(
            "Package name", "", self.input_done, None, None)

    def input_done(self, text):
        try:
            module_path = find_module_path(text, self.py2)
            open_in_new_window(module_path)
        except subprocess.CalledProcessError:
            sublime.status_message("Not found: {}".format(e))


class open_module_py2(open_module):
    py2 = True


def find_module_path(text, py2=False):
    " Try to find the filesystem location of a Python module. "
    text = text.splitlines()[0]
    text = non_alphanum.sub('', text)
    env = {"PATH": PATH} if PATH else None
    module_path = subprocess.check_output([
        "python2" if py2 else "python3",
        "-c",
        "import imp;print(imp.find_module('{}')[1])".format(text)], env=env)
    return module_path.decode('utf8').strip()


def open_in_new_window(path):
    " Open a path in a new ST3 window by invoking the subl cli utility "
    # https://github.com/titoBouzout/SideBarEnhancements/blob/st3/SideBar.py#L1643
    executable_path = sublime.executable_path()
    if sublime.platform() == 'osx':
        app_path = executable_path[:executable_path.rfind(".app/") + 5]
        executable_path = app_path + "Contents/SharedSupport/bin/subl"

    env = {"PATH": PATH} if PATH else None
    subprocess.Popen([executable_path, path], env=env)
