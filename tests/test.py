# encoding: utf-8
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Author: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from __future__ import unicode_literals
from __future__ import absolute_import

from mo_dots import Data
from mo_testing.fuzzytestcase import FuzzyTestCase

from parse import parse_diff


class TestParsing(FuzzyTestCase):

    def test_parse(self):
        result = parse_diff(Data(url="https://hg.mozilla.org/integration/mozilla-inbound"), changeset_id="17f8bf61f6e9")

        expected = {

        }

        self.assertEqual(result, expected)


