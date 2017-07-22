# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import absolute_import
from __future__ import unicode_literals

import numpy as np
from mo_files import File
from mo_testing.fuzzytestcase import FuzzyTestCase

from parse import parse_diff_to_matrix


class TestParsing(FuzzyTestCase):
    def test_parse(self):
        # file1 -> c1 -> file2 -> c2 -> file3

        file1 = File("tests/resources/example_file_v1.py").read().split('\n')
        file2 = File("tests/resources/example_file_v2.py").read().split('\n')
        file3 = File("tests/resources/example_file_v3.py").read().split('\n')

        c1 = parse_diff_to_matrix(
            diff=File("tests/resources/diff1.patch").read(),
            new_source_code=file2
        )["/tests/resources/example_file.py"]

        c2 = parse_diff_to_matrix(
            diff=File("tests/resources/diff2.patch").read(),
            new_source_code=file3
        )["/tests/resources/example_file.py"]

        coverage2 = np.array([1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0], dtype=int).T

        coverage1 = np.dot(coverage2, c1.T)
        coverage3 = np.dot(coverage2, c2)

        self.assertEqual(coverage1, [1, 1, 0, 1,       0, 1, 1, 1, 0])
        self.assertEqual(coverage2, [1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0])
        self.assertEqual(coverage3, [1, 0, 0, 0, 0])
