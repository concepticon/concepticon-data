from pyconcepticon import Concepticon


def test_data():
    api = Concepticon('.')
    assert api.check()
    assert len(api.union('Swadesh-1952-200', 'Swadesh-1955-100')) == 207 

