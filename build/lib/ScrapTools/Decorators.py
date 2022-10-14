"""A file to define some useful decorators for scraping"""

import time as tm


class ToManyTry(Exception):
    pass


def retry(function):
    """
    A decorator aimed to retry 3 times if execution of function failed.
    We wait 3 seconds between each try
    """

    def wraper(*args, **kwargs):
        i = 0
        MAX_ITER = 3
        while i < MAX_ITER:
            try:
                res = function(*args, **kwargs)
                return res
            except Exception as e:
                print(e, f"\n\n [{i}]An error occur, retrying")
                i += 1
                tm.sleep(2)
        raise ToManyTry("Even after 3 try it is not working")

    return wraper
