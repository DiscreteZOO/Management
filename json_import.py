#!/usr/bin/env python

import os
import sys
import json
import settings

def import_changes(location, path):
    p = path
    l = []
    for i in range(3):
        p, last = os.path.split(p)
        l.append(last)
    objs = os.path.join(location, "objects")
    dest = os.path.join(objs, *reversed(l))
    with open(path) as f:
        d = json.load(f)
    exists = os.path.exists(dest)
    if exists:
        with open(dest) as f:
            obj = json.load(f)
    else:
        obj = d
    for k, v in d.items():
        if k in obj:
            obj[k].update(v)
        else:
            obj[k] = v
        if "_delete" in v:
            for f, x in v["_delete"].items():
               if isinstance(obj[k][f], dict):
                   for t in x:
                       del obj[k][f][t]
               else:
                   obj[k][f] = sorted(t for t in obj[k][f] if t not in x)
            del obj[k]["_delete"]
        if "_add" in v:
            for f, x in v["_add"].items():
               if isinstance(obj[k][f], dict):
                   obj[k][f].update(x)
               else:
                   obj[k][f] += x
                   obj[k][f].sort()
            del obj[k]["_add"]
    with open(dest, "w") as f:
        json.dump(obj, f, indent = 4, sort_keys = True)
    if not exists:
        algo, uid = l[2], l[1] + l[0]
        for a, u in d["object"]["unique_id"].items():
            if (a, u) == (algo, uid):
                continue
            os.symlink(os.path.join("..", "..", *reversed(l)),
                       os.path.join(objs, a, u[:2], u[2:]))

if __name__ == "__main__":
    for path in sys.argv[1:]:
        import_changes(settings.DATA_REPO, path)
