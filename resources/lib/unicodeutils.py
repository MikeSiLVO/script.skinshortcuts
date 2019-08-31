import sys


def try_decode(text, encoding="utf-8"):
    if sys.version_info.major == 3:
        if not isinstance(text, str):
            try:
                return text.decode(encoding)
            except:
                pass
        return text
    else:
        if isinstance(text, str):
            try:
                return text.decode(encoding)
            except:
                pass
        return text