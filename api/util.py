def int_without_exception(text: str, default=0):
    if not isinstance(text, str):
        return default
    clear = ''
    for i in text:
        if i in '0123456789':
            clear += i
    try:
        return int(clear)
    except:
        return default