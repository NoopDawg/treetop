import os
import glob
import readline


def _path_completer(text, state):
    expanded = os.path.expanduser(text)
    matches = glob.glob(expanded + "*")
    matches = [
        (m + os.sep if os.path.isdir(m) else m)
        for m in matches
    ]
    if text.startswith("~"):
        home = os.path.expanduser("~")
        matches = [m.replace(home, "~", 1) for m in matches]
    return matches[state] if state < len(matches) else None


def input_with_path_completion(prompt):
    old_completer = readline.get_completer()
    old_delims = readline.get_completer_delims()

    readline.set_completer_delims(old_delims.replace("/", "").replace("~", ""))
    readline.set_completer(_path_completer)

    if "libedit" in (readline.__doc__ or ""):
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

    try:
        return input(prompt)
    finally:
        readline.set_completer(old_completer)
        readline.set_completer_delims(old_delims)
