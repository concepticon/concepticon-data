from pyconcepticon import Concepticon


def test_data():
    api = Concepticon('.')
    assert api.check()

