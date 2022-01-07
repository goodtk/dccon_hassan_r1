def combine_words(args):
    shortcut_name = ''

    for i, arg in enumerate(args):
        shortcut_name += arg + ' '

    return shortcut_name.strip()