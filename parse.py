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

from mo_logs import Log
from mo_logs.strings import expand_template
from numpy import copy
from pyLibrary.env import http
from BeautifulSoup import BeautifulSoup
import numpy as np

GET_DIFF = "{{location}}/rev/{{rev}}"
GET_FILE = "{{location}}/file/{{rev}}{{path}}"

HUNK_HEADER = re.compile(r"^-(\d+),(\d+) \+(\d+),(\d+) @@.*")
FILE_SEP = re.compile(r"^--- ", re.MULTILINE)
HUNK_SEP = re.compile(r"^@@ ", re.MULTILINE)

MOVE = {
    ' ': np.array([1, 1], dtype=int),
    '+': np.array([1, 0], dtype=int),
    '-': np.array([0, 1], dtype=int)
}
no_change = MOVE[' ']


def parse_diff(branch, changeset_id):
    """
    :param branch: OBJECT TO DESCRIBE THE BRANCH TO PULL INFO
    :param changeset_id: THE REVISION NUMEBR OF THE CHANGESET
    :return:  MAP FROM FULL PATH TO OPERATOR
    """
    output = {}

    response = http.get(expand_template(GET_DIFF, {"location": branch.url, "rev": changeset_id}))

    doc = BeautifulSoup(response.content)
    changeset = "".join(unicode(l) for t in doc.findAll("pre", {"class": "sourcelines"}) for l in t.findAll(text=True))

    files = FILE_SEP.split(changeset)
    for file in files:
        if not file.strip():
            continue
        file_header_a, file_header_b, file_diff = file.split("\n", 2)
        file_path = file_header_a[1:]  # eg file_header_a == "a/testing/marionette/harness/marionette_harness/tests/unit/unit-tests.ini"

        coord = []
        c = np.array([0,0], dtype=int)
        for hunk in HUNK_SEP.split(file_diff):
            if not hunk:
                continue
            line_diffs = hunk.split("\n")
            old_start, old_length, new_start, new_length = HUNK_HEADER.match(line_diffs[0]).groups()
            next_c = np.array([new_start, old_start], dtype=int)
            if next_c[0] - next_c[1] != c[0] - c[1]:
                Log.error("expecting a skew of {{skew}}", skew=next_c[0] - next_c[1])
            if c[0] >= next_c[0]:
                Log.error("can not hanlde out-of-order diffs")
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

        response = http.get(expand_template(GET_FILE, {"location": branch.url, "rev": changeset_id, "path": file_path}))
        doc = BeautifulSoup(response.content)
        code = "".join(unicode(l) for t in doc.findAll("pre", {"class": "sourcelines stripes"}) for l in t.findAll(text=True)).split("\n")

        new_length = len(code)
        maxx = np.max(coord, 0)
        old_length = new_length + (maxx[1] - maxx[0])
        matrix = np.zeros((new_length + 1, old_length + 1), dtype=np.uint8)
        matrix[zip(*coord)] = 1

        output[file_path] = matrix
    return output
