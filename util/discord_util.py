def is_called_by_slash(ctx):
    try:
        if ctx.slash:
            return True
    except:
        pass
    return False