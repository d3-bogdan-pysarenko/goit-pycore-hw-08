import functools
def input_error(func):
    """
    Decorator for caching user's input errors like KeyError, ValueError, IndexError
    """
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Wrong parameters are provided, please try again with valid data"
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter user name."
    return inner