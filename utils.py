#############################################################################
##
##                            UTILITY FUNCTIONS
##
##                            Milan Rother 2023
##
#############################################################################

# IMPORTS ===================================================================

from functools import wraps
from time import perf_counter


# MISC =====================================================================

def timer(func):
    """
    shows the execution time 
    of the function object passed
    """
    def wrap_func(*args, **kwargs):

        t1 = perf_counter()
        result = func(*args, **kwargs)
        t2 = perf_counter()

        print(f'Function {func.__name__!r} executed in {(t2-t1)*1e3:.2f}ms')

        return result

    return wrap_func
