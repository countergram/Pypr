import subprocess
from .env import env


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


get_module_list_script = r"""\
import pkgutil
import os

valid_names = [
    name for (loader, name, is_pkg) in pkgutil.iter_modules()
    if hasattr(loader, 'path') and (
        os.path.isfile(os.path.join(loader.path, name) + ".py")
        or os.path.isdir(os.path.join(loader.path, name))
    )
]

print("\n".join(valid_names))
"""


def get_module_list(py2=False):
    " List of names of available modules for an interpreter "
    try:
        raw_output = subprocess.check_output([
            "python2" if py2 else "python3",
            "-c",
            get_module_list_script], env=env(), stderr=subprocess.STDOUT)
        module_names = [
            line.decode('utf8').strip()
            for line in raw_output.splitlines() if line]
        # Sort names case-insensitive and underbar-names to bottom
        module_names.sort(key=str.upper)
        return module_names
    except subprocess.CalledProcessError as exc:
        print("[Pypr] Error when calling python")
        print(exc.output)
        return []
