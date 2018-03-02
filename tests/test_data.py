from pyconcepticon.check_data import check


def test():
    if not check():
        raise ValueError('integrity checks failed!')
