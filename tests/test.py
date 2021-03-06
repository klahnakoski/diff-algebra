# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import numpy as np
from mo_dots import wrap
from mo_files import File
from mo_json import value2json
from mo_logs import constants, Log, startup
from mo_testing.fuzzytestcase import FuzzyTestCase

from mo_hg.hg_mozilla_org import HgMozillaOrg
from mo_hg.parse import diff_to_json
from parse import parse_diff_to_matrix


class TestParsing(FuzzyTestCase):

    @classmethod
    def setUpClass(cls):
        try:
            cls.config = startup.read_settings()
            constants.set(cls.config.constants)
            Log.start(cls.config.debug)
        except Exception as e:
            Log.error("Problem with etl", e)

    @classmethod
    def tearDownClass(cls):
        Log.stop()

    def setUp(self):
        self.hg = HgMozillaOrg(TestParsing.config)

    def _get_test_data(self):
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

        # file1 -> c1 -> file2 -> c2 -> file3
        return file1, c1, file2, c2, file3

    def test_parse(self):
        file1, c1, file2, c2, file3 = self._get_test_data()

        coverage2 = np.matrix([1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0], dtype=int)

        coverage1 = coverage2 * c1.T
        coverage3 = coverage2 * c2

        self.assertEqual(coverage1.tolist(), [[1, 1, 0, 1,       0, 1, 1, 1, 0, 0]])
        self.assertEqual(coverage2.tolist(), [[1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0]])
        self.assertEqual(coverage3.tolist(), [[1, 1, 0, 1, 1, 0, 0, 0, 0]])

    def test_diff_to_json(self):
        j1 = diff_to_json(File("tests/resources/diff1.patch").read())
        j2 = diff_to_json(File("tests/resources/diff2.patch").read())

        e1 = File("tests/resources/diff1.json").read_json(flexible=False, leaves=False)
        e2 = File("tests/resources/diff2.json").read_json(flexible=False, leaves=False)
        self.assertEqual(j1, e1)
        self.assertEqual(j2, e2)

    def test_big_changeset_to_json(self):
        j1 = diff_to_json(File("tests/resources/big.patch").read())
        expected = File("tests/resources/big.json").read_json(flexible=False, leaves=False)
        self.assertEqual(j1, expected)

    def test_changeset_to_json(self):
        j1 = self.hg.get_revision(
            wrap({
                "branch": {"name": "mozilla-central", "url": "https://hg.mozilla.org/mozilla-central"},
                "changeset": {"id": "e5693cea1ec944ca0"}
            }),
            None,  # Locale
            True   # get_diff
        )
        expected = File("tests/resources/big.json").read_json(flexible=False, leaves=False)
        self.assertEqual(j1.changeset.diff, expected)

    def test_net_new_lines(self):
        file1, c1, file2, c2, file3 = self._get_test_data()

        # NET NEW LINES CAN BE EXTRACTED FROM A CHANGESET 1==New line, 0==Old line
        net_new_lines = (- np.sum(c1, 0)) + 1  # MAYBE THIS SHOULD BE A FUNCTION CALLED net_new_lines(changeset)

        self.assertEqual(net_new_lines.tolist(), [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0])

    def test_net_new_percent(self):
        file1, c1, file2, c2, file3 = self._get_test_data()

        net_new_lines2 = (- np.sum(c1, 0)) + 1  # MAYBE THIS SHOULD BE A FUNCTION CALLED net_new_lines(changeset)
        num_net_new_lines = np.sum(net_new_lines2)

        coverage2 = np.array([1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0], dtype=int)
        # MULTIPLY net_new_lines WITH THE coverage2 VECTOR TO GET INTERSECTION
        # sum THE INTERSECTION TO GET A COUNT
        # MAYBE WE SHOULD BE USING BOOLEAN ARRAYS EVERYWHERE
        num_net_new_lines_covered = np.sum(coverage2 * net_new_lines2)

        net_new_percent = num_net_new_lines_covered / num_net_new_lines
        self.assertEqual(net_new_percent, 0.5)

    def test_percent_using_future_coverage(self):
        file1, c1, file2, c2, file3 = self._get_test_data()

        # WE ARE GIVEN FUTURE COVERAGE
        coverage3 = np.matrix([1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=int)
        # CALCULATE THE COVERAGE FOR REVISION 2
        coverage2 = coverage3 * c2.T
        # THE NET NEW LINES FOR REVISION 2
        net_new_lines2 = np.matrix((- np.sum(c1, 0)) + 1)  # THE MATRIX WILL ALLOW TRANSPOSES
        num_net_new_lines_covered = np.sum(coverage2 * net_new_lines2.T)

        net_new_percent = num_net_new_lines_covered / np.sum(net_new_lines2)
        self.assertEqual(net_new_percent, 1)


