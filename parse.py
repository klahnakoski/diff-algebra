import HTMLParser
from BeautifulSoup import BeautifulSoup, SoupStrainer
from mo_times import Timer
    '\\': np.array([0, 0], dtype=int),  # FOR "\ no newline at end of file"
def parse_changeset_to_matrix(branch, changeset_id, new_source_code=None):
    unescape = HTMLParser.HTMLParser().unescape
    with Timer("parsing http diff"):
        doc = BeautifulSoup(
            response.content,
            parseOnlyThese=SoupStrainer("pre", {"class": "sourcelines"})
        )
    changeset = "".join(unescape(unicode(l)).rstrip("\r") for l in doc.findAll(text=True))
def changeset_to_json(branch, changeset_id, new_source_code=None):
    diff = _get_changeset(branch, changeset_id)
    return diff_to_json(diff)


def diff_to_json(changeset):
    files = FILE_SEP.split(changeset)[1:]
    for file_ in files:
        hunks = HUNK_SEP.split(file_diff)[1:]
        for hunk in hunks:
            next_c = np.array([max(0, int(new_start)-1), max(0, int(old_start)-1)], dtype=int)
                if line.startswith("new file mode")or line.startswith("deleted file mode"):
                    # HAPPENS AT THE TOP OF NEW FILES
                    # u'new file mode 100644'
                    # u'deleted file mode 100644'
                    break
                    changes.append({"new": {"line": int(c[0]), "content": line[1:]}})
                    changes.append({"old": {"line": int(c[1]), "content": line[1:]}})
                try:
                    c += MOVE[d]
                except Exception as e:
                    Log.warning("bad line {{line|quote}}", line=line, cause=e)