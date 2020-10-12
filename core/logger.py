def logger(func):
    def function(*func_args, **func_kwargs):
        print('run: {}'.format(func.__name__))
        return func(*func_args, **func_kwargs)
    return function