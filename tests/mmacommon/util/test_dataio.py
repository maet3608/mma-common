"""
.. module:: dataio
   :synopsis: Unit tests for dataio module
"""
import mmacommon.util.dataio as dio
import pytest


def test_load_tsv():
    rows = dio.load_tsv('tests/data/data.tsv')
    assert next(rows) == ['this', 'is a', 'test']
    assert next(rows) == ['next', 'row']
    with pytest.raises(StopIteration) as ex:
        next(rows)


def test_load_csv():
    rows = dio.load_csv('tests/data/data.csv')
    assert next(rows) == ['this', 'is a', 'test']
    assert next(rows) == ['next', 'row']
    with pytest.raises(StopIteration) as ex:
        next(rows)
