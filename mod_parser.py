import subprocess
from pathlib import Path
import os, sys

def cli_run(cmd: str):
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) as p:
        if p.returncode != None and p.returncode != 0:
            raise ValueError(f"'{cmd}' failed, returncode {p.returncode}")
        std = str(p.stdout.read(), 'utf-8')
        return std

prefix = "github.com/curtisnewbie"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Specify where the root directory is:")
        sys.exit(0)

    project_list = [
        # "goauth"
        # "gocommon",
        # "hammer",
        # "doc-indexer",
        # "postbox",
        "miso",
        "gatekeeper",
        "vfm",
        "user-vault",
        "event-pump",
        "logbot",
        "mini-fstore",
        "acct"
    ]

    rootdir = sys.argv[1]
    rootpath = Path(rootdir).absolute()
    project_inf = []

    miso_found = False
    for d in rootpath.iterdir():
        if not d.is_dir(): continue
        for pl in project_list:
            plp = str(rootpath) + os.sep + pl
            dp = str(d)
            if dp == plp:
                if pl == "miso":
                    miso_found = True
                project_inf.append({
                    "name": pl,
                    "dir" : plp,
                    "mod": "",
                    "dependencies": [],
                })
                break
    if not miso_found:
        project_inf.append({
            "name": "miso",
            "dir": "",
            "mod": "",
            "dependencies": []
        })

    for inf in project_inf:
        p = inf["dir"]
        if not p: continue
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
        if inf['mod']:
            with open(inf['mod']) as fi:
                li = fi.readlines()
                for l in li:
                    l = l.strip()
                    if l.startswith(prefix):
                        inf["dependencies"].append(l)

    # for inf in project_inf: print(inf)

    digraph = "digraph \"[dependencies]\" {\n"
    digraph += "pad=0.5\n"
    digraph += "fontname=\"Helvetica,Arial,sans-serif\"\n"
    digraph += "node [fontname=\"Helvetica,Arial,sans-serif\"]\n"
    digraph += "edge [fontname=\"Helvetica,Arial,sans-serif\"]\n"
    digraph += "node [style=filled fillcolor=\"#f8f8f8\"]\n"

    ni = 1
    nodes = {}
    for inf in project_inf:
        nodes[inf["name"]] = ni
        name = inf['name']
        digraph +=f'N{ni} [label="{name}" id="node{ni}" fontsize=8 shape=box tooltip="github.com/curtisnewbie/{name}" color="#b20400" fillcolor="#edd6d5"]\n'
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
            if project not in nodes: continue
            to = nodes[project]
            lver = ver
            if len(lver) > 15:
                lver = lver[:12] + "..."
            digraph +=f'N{curr} -> N{to} [label=" {lver}" labelfloat=false fontsize=6 weight=1 color="#b2a999" tooltip="{project} {ver}" labeltooltip="{project} {ver}"]\n'

    digraph += "}\n"
    # print(digraph)

    with open("/tmp/dp_out.txt", "+w") as f:
        f.write(digraph)

    print(cli_run("dot -Gdpi=300 -Tpng /tmp/dp_out.txt > /tmp/dpout.png && open /tmp/dpout.png"))

    # python3 mod_parser.py ~/dev/git
