import subprocess
import sublime
import sublime_plugin
from .modules import get_module_list, find_module_path
from .env import env


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


def open_in_new_window(path):
    " Open a path in a new ST3 window by invoking the subl cli utility "
    # https://github.com/titoBouzout/SideBarEnhancements/blob/st3/SideBar.py#L1643
    executable_path = sublime.executable_path()
    if sublime.platform() == 'osx':
        app_path = executable_path[:executable_path.rfind(".app/") + 5]
        executable_path = app_path + "Contents/SharedSupport/bin/subl"
    subprocess.Popen([executable_path, path], env=env())
