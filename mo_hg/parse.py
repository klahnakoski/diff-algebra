from mo_dots import wrap
from mo_logs import Log, strings

MAX_CONTENT_LENGTH = 500  # SOME "lines" FOR CODE ARE REALLY TOO LONG
                    changes.append({"new": {"line": int(c[0]), "content": strings.limit(line[1:], MAX_CONTENT_LENGTH)}})
                    changes.append({"old": {"line": int(c[1]), "content": strings.limit(line[1:], MAX_CONTENT_LENGTH)}})
    return wrap(output)