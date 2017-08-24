# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals

import re

import numpy as np
from mo_logs import Log
from numpy import copy

GET_DIFF = "{{location}}/rev/{{rev}}"
GET_FILE = "{{location}}/file/{{rev}}{{path}}"

HUNK_HEADER = re.compile(r"^-(\d+),(\d+) \+(\d+),(\d+) @@.*")
FILE_SEP = re.compile(r"^--- ", re.MULTILINE)
HUNK_SEP = re.compile(r"^@@ ", re.MULTILINE)

MOVE = {
    ' ': np.array([1, 1], dtype=int),
    '\\': np.array([0, 0], dtype=int),  # FOR "\ no newline at end of file"
    '+': np.array([1, 0], dtype=int),
    '-': np.array([0, 1], dtype=int)
}
no_change = MOVE[' ']


def parse_changeset_to_matrix(branch, changeset_id, new_source_code=None):
    """
    :param branch:  Data with `url` parameter pointing to hg instance 
    :param changeset_id:   
    :param new_source_code:  for testing - provide the resulting file (for file length only) 
    :return: 
    """
    diff = _get_changeset(branch, changeset_id)
    map = _parse_diff(diff, new_source_code)
    return _map_to_matrix(map)


def parse_diff_to_matrix(diff, new_source_code=None):
    """
    :param diff:  textual diff 
    :param new_source_code:  for testing - provide the resulting file (for file length only) 
    :return: 
    """
    return _map_to_matrix(_parse_diff(diff, new_source_code))


def _map_to_matrix(map):
    output = {}
    for file_path, coord in map.items():
        maxx = np.max(coord, 0)
        matrix = np.zeros(maxx + 1, dtype=np.uint8)
        matrix[zip(*coord)] = 1
        output[file_path] = matrix.T  # OOPS! coordinates were reversed
    return output


def parse_to_map(branch, changeset_id):
    """
    MATRICIES ARE O(n^2), WE NEED A O(n) SOLUTION
    
    :param branch: OBJECT TO DESCRIBE THE BRANCH TO PULL INFO
    :param changeset_id: THE REVISION NUMEBR OF THE CHANGESET
    :return:  MAP FROM FULL PATH TO OPERATOR
    """

    map = _parse_diff(_get_changeset(branch, changeset_id))
    output = {}
    for file_path, coord in map.items():
        maxx = np.max(coord, 0)
        matrix = np.zeros(maxx + 1, dtype=np.uint8)
        matrix[zip(*coord)] = 1
        output[file_path] = matrix.T
    return output


def _parse_diff(changeset, new_source_code=None):
    """
    :param branch: OBJECT TO DESCRIBE THE BRANCH TO PULL INFO
    :param changeset: THE DIFF TEXT CONTENT
    :param new_source_code:  for testing - provide the resulting file (for file length only) 
    :return:  MAP FROM FULL PATH TO LIST OF COORINATES
    """
    output = {}

    files = FILE_SEP.split(changeset)
    for file in files[1:]:
        file_header_a, file_header_b, file_diff = file.split("\n", 2)
        file_path = file_header_a[1:]  # eg file_header_a == "a/testing/marionette/harness/marionette_harness/tests/unit/unit-tests.ini"

        coord = []
        c = np.array([0,0], dtype=int)
        for hunk in HUNK_SEP.split(file_diff)[1:]:
            line_diffs = hunk.split("\n")
            old_start, old_length, new_start, new_length = HUNK_HEADER.match(line_diffs[0]).groups()
            next_c = np.array([int(new_start)-1, int(old_start)-1], dtype=int)
            if next_c[0] - next_c[1] != c[0] - c[1]:
                Log.error("expecting a skew of {{skew}}", skew=next_c[0] - next_c[1])
            if c[0] > next_c[0]:
                Log.error("can not handle out-of-order diffs")
            while c[0] != next_c[0]:
                coord.append(copy(c))
                c += no_change

            for line in line_diffs[1:]:
                if not line:
                    continue
                d = line[0]
                if d == ' ':
                    coord.append(copy(c))
                c += MOVE[d]

        # WE ONLY NEED THE NUMBER OF CODE LINES SO WE KNOW THE CODE DIMENSIONS SO WE CAN MAKE THE MATRIX
        # A MORE EFFICIENT IMPLEMENTATION COULD WORK WITHOUT KNOWING THE LENGTH OF THE SOURCE
        if new_source_code is None:
            new_length = len(get_source_code(branch, changeset_id, file_path))
        else:
            new_length = len(new_source_code)

        while c[0] < new_length:
            coord.append(copy(c))
            c += no_change

        output[file_path] = coord
    return output
