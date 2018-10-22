"""
.. module:: dataio
   :synopsis: Basic data IO operations such as saving, loading and encoding.
"""

import csv


def load_tsv(filepath):
    """
    Load file with Tab Separated Values.

    Skip empty lines and remove leading and trailing spaces from values.

    :param str filepath: Path to file.
    :return: List of values for each line in file.
    :rtype: Generator over lists of values.
    """
    with open(filepath) as f:
        for line in f:
            row = [value.strip() for value in line.split('\t')]
            if row != ['']:
                yield row


def load_csv(filepath):
    """
    Load file with Comma Separated Values.

    A very thin wrapper around the corresponding function within the
    Python csv module. In addition it removes leading and trailing
    whitespaces from values and skips empty lines.

    :param str filepath: Path to file.
    :return: List of values for each line in file.
    :rtype: Generator over lists of values.
    """
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            row = [v.strip() for v in row]
            if row and row != ['']:
                yield row
