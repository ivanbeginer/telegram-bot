from collections.abc import Callable

def filter_for_command(command:str):
    return lambda callback_data:callback_data[0]==command