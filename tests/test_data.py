from pyconcepticon.check_data import check


def test_data():
    if not check():
        raise ValueError('integrity checks failed!')
