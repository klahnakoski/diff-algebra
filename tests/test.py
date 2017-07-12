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

from mo_dots import Data
from mo_testing.fuzzytestcase import FuzzyTestCase

from parse import parse_to_matrix


class TestParsing(FuzzyTestCase):

    def test_parse(self):
        result = parse_to_matrix(Data(url="https://hg.mozilla.org/integration/mozilla-inbound"), changeset_id="17f8bf61f6e9")

        expected = {

        }

        self.assertEqual(result, expected)


