from pathlib import Path
import os, sys

prefix = "github.com/curtisnewbie"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Specify where the root directory is:")
        sys.exit(0)

    project_list = [
        "postbox",
        "miso",
        "gatekeeper",
        "vfm",
        "user-vault",
        "hammer",
        "event-pump",
        "doc-indexer",
        "logbot",
        "gocommon",
        "mini-fstore",
        "goauth"
    ]

    rootdir = sys.argv[1]
    rootpath = Path(rootdir).absolute()
    project_inf = []

    for d in rootpath.iterdir():
        if not d.is_dir(): continue
        for pl in project_list:
            plp = str(rootpath) + os.sep + pl
            dp = str(d)
            if dp == plp:
                project_inf.append({
                    "name": pl,
                    "dir" : plp,
                    "mod": "",
                    "dependencies": [],
                })
                break

    for inf in project_inf:
        p = inf["dir"]
        found = False
        for f in os.listdir(p):
            if f == "go.mod":
                modf = p + os.sep + f
                inf["mod"] = modf
                found = True
                break
        if not found:
            raise ValueError("go.mod not found")

    # for inf in project_inf: print(inf)

    for inf in project_inf:
        with open(inf['mod']) as fi:
            li = fi.readlines()
            for l in li:
                l = l.strip()
                if l.startswith(prefix):
                    inf["dependencies"].append(l)

    # for inf in project_inf: print(inf)

    digraph = "digraph \"[dependencies]\" {\n"
    digraph += "fontname=\"Helvetica,Arial,sans-serif\"\n"
    digraph += "node [fontname=\"Helvetica,Arial,sans-serif\"]\n"
    digraph += "edge [fontname=\"Helvetica,Arial,sans-serif\"]\n"
    digraph += "node [style=filled fillcolor=\"#f8f8f8\"]\n"

    ni = 1
    nodes = {}
    for inf in project_inf:
        nodes[inf["name"]] = ni
        name = inf['name']
        digraph +=f'N{ni} [label="{name}" id="node{ni}" fontsize=18 shape=box tooltip="github.com/curtisnewbie/{name}" color="#b20400" fillcolor="#edd6d5"]\n'
        ni+=1

    for inf in project_inf:
        curr = nodes[inf["name"]]
        dependencies = inf['dependencies']
        for d in dependencies:
            j = d.rfind(prefix)
            k = d.rfind("v")
            ver = d[k:]
            project = d[len(prefix) + 1:k].strip()
            # print(ver)
            # print(project)
            to = nodes[project]
            digraph +=f'N{curr} -> N{to} [label="{ver}" weight=1 color="#b2a999" tooltip="{project} {ver}" labeltooltip="{project} {ver}!"]\n'

    digraph += "}\n"
    print(digraph)

    # python3 mod_parser.py ~/dev/git > test.txt && gen_graph test.txt && open out.svg
    # e.g.,
    # python3 mod_parser.py ~/dev/git > est.txt && dot -Tsvg test.txt > out.svg && open out.svg
