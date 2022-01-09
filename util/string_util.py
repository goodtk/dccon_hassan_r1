def combine_words(args):
    keyword = ''

    for i, arg in enumerate(args):
        keyword += arg + ' '

    return keyword.strip()