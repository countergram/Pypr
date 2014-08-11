PATH = None


def env():
    " Return an environment to pass to subprocess "
    return {"PATH": PATH} if PATH else None
