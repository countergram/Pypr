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


def env():
    " Return an environment to pass to subprocess "
    return {"PATH": PATH} if PATH else None


class open_module(sublime_plugin.WindowCommand):

    " Prompt for a package name and attempt to load the file or dir "

    py2 = False

    def run(self):
        self.modules = get_module_list(self.py2)
        self.window.show_quick_panel(self.modules, self.input_done)

    def input_done(self, index):
        if index == -1:
            return
        text = self.modules[index]
        try:
            module_path = find_module_path(text, self.py2)
            open_in_new_window(module_path)
        except subprocess.CalledProcessError:
            sublime.status_message("Not found: {}".format(text))


class open_module_py2(open_module):
    py2 = True


find_module_path_script = r"""\
import imp
print(imp.find_module('{}')[1])
"""


def find_module_path(text, py2=False):
    " Try to find the filesystem location of a Python module. "
    module_path = subprocess.check_output([
        "python2" if py2 else "python3",
        "-c",
        find_module_path_script.format(text)], env=env())
    return module_path.decode('utf8').strip()


def open_in_new_window(path):
    " Open a path in a new ST3 window by invoking the subl cli utility "
    # https://github.com/titoBouzout/SideBarEnhancements/blob/st3/SideBar.py#L1643
    executable_path = sublime.executable_path()
    if sublime.platform() == 'osx':
        app_path = executable_path[:executable_path.rfind(".app/") + 5]
        executable_path = app_path + "Contents/SharedSupport/bin/subl"
    subprocess.Popen([executable_path, path], env=env())


get_module_list_script = r"""\
import pkgutil
import os

valid_names = [
    name for (loader, name, is_pkg) in pkgutil.iter_modules()
    if os.path.isfile(os.path.join(loader.path, name) + ".py")
    or os.path.isdir(os.path.join(loader.path, name))
]

print("\n".join(valid_names))
"""


def get_module_list(py2=False):
    " List of names of available modules for an interpreter "
    raw_output = subprocess.check_output([
        "python2" if py2 else "python3",
        "-c",
        get_module_list_script], env=env())
    module_names = [
        line.decode('utf8').strip()
        for line in raw_output.splitlines() if line]
    # Sort names case-insensitive and underbar-names to bottom
    module_names.sort(key=str.upper)
    return module_names
