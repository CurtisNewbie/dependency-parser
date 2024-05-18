from pathlib import Path
import os, sys
import json
import subprocess

def cli_run(cmd: str):
    with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE) as p:
        if p.returncode != None and p.returncode != 0:
            raise ValueError(f"'{cmd}' failed, returncode {p.returncode}")
        std = str(p.stdout.read(), 'utf-8')
        return std

"""
    python3 tree_parser.py /dir/myproject
"""
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Where is the project?")
        sys.exit(0)

    root = ""
    if len(sys.argv) > 2: root = sys.argv[2]

    fp = sys.argv[1]
    fpc = cli_run(f"mvn dependency:tree -f {fp}")
    print(fpc)
    lines = fpc.splitlines()

    # with open("treeout.txt") as f: lines = f.readlines()

    seg = []
    inseg = False
    st = 0
    ed = 0
    for i in range(len(lines)):
        l = lines[i]
        if not inseg and l.startswith("[INFO] --- dependency:"):
            inseg = True
            st = i
        elif inseg and (l.strip() == "[INFO]" or l.startswith("[INFO] ----")):
            inseg = False
            ed = i
            seg.append(lines[st+1:ed])

    debug = ""
    project_inf = {  }
    for se in seg:
        curr_layer = 0
        parents = []
        for l in se:
            l = l.strip()
            if l == "": continue
            if l.endswith(":test"): continue

            l = l[7:] # "[INFO] "
            idt = 0
            for i in range(len(l)):
                c: str = l[i]
                # print("c: ", c)
                if c in ["+", "-", " ",  "|", "\\"]:
                    idt += 1
                else:
                    break

            layer = 0
            if idt > 0:
                layer = int(idt / 3)

            l = l[idt:]
            if l.endswith(":compile"): l = l[:len(l) - len(":compile")]
            if l.endswith(":runtime"): l = l[:len(l) - len(":runtime")]

            # print(curr_layer, layer, idt, parents)
            pa = None
            if len(parents) > 0: pa = parents[len(parents) - 1]
            debug += f"curr_layer: {curr_layer}, layer: {layer}, idt: {idt}, parent: {pa}, lenp: {len(parents)}, {l}\n"

            if len(parents) < 1:
                n = l.strip()
                v = None
                if n in project_inf:
                    v = project_inf[n]
                else:
                    v = { "name": n, "dependencies": [], "layer": layer }
                    project_inf[n] = v

                parents.append(v)
                curr_layer = layer
            else:
                if layer <= curr_layer:
                    n = l.strip()
                    parents.pop()

                    while len(parents) > 1 and layer <= parents[len(parents) - 1]["layer"]:
                        parents.pop()

                    p = parents[len(parents) - 1]
                    if n not in p["dependencies"]: p["dependencies"].append(n)

                    v = None
                    if n in project_inf: v = project_inf[n]
                    else:
                        v = { "name": n, "dependencies": [], "layer": layer }
                        project_inf[n] = v

                    parents.append(v)
                    curr_layer = layer

                elif layer > curr_layer:
                    n = l.strip()
                    p = parents[len(parents) - 1]
                    if n not in p["dependencies"]: p["dependencies"].append(n)

                    v = None
                    if n in project_inf: v = project_inf[n]
                    else:
                        v = { "name": n, "dependencies": [], "layer": layer }
                        project_inf[n] = v

                    parents.append(v)
                    curr_layer = layer
                else:
                    n = l.strip()
                    p = parents[len(parents) - 1]
                    if n not in p["dependencies"]: p["dependencies"].append(n)
                    if n not in project_inf: project_inf[n] = { "name": n, "dependencies": [], "layer": layer }

    with open("out.json", "w+") as f: f.write(json.dumps(project_inf))
    with open("debug.log", "w+") as f: f.write(debug)

    # for inf in project_inf: print(inf)

    digraph = "digraph \"[dependencies]\" {\n"
    digraph += "pad=0.5\n"
    digraph += "nodesep=1.5\n"
    digraph += "ranksep=1.5\n"
    digraph += "overlap=false\n"
    # digraph += "splines=ortho\n"
    # digraph += "layout=circo\n"
    digraph += "rankdir=TB\n"
    digraph += "fontname=\"Helvetica,Arial,sans-serif\"\n"
    digraph += "node [fontname=\"Helvetica,Arial,sans-serif\"]\n"
    digraph += "edge [fontname=\"Helvetica,Arial,sans-serif\"]\n"
    digraph += "node [style=filled fillcolor=\"#f8f8f8\"]\n"

    if not root:
        ni = 1
        nodes = {}
        for k in project_inf:
            inf = project_inf[k]
            nodes[inf["name"]] = { "idx" : ni }
            name = inf['name']
            digraph +=f'N{ni} [label="{name}" id="node{ni}" fontsize=8 shape=box color="#b20400" fillcolor="#edd6d5"]\n'
            ni+=1

        for k in project_inf:
            inf = project_inf[k]
            curr = nodes[inf["name"]]
            curr_idx = curr["idx"]
            dependencies = inf['dependencies']
            for d in dependencies:
                if d not in nodes: continue
                to = nodes[d]
                to_idx = to["idx"]
                digraph +=f'N{curr_idx} -> N{to_idx} [label="" labelfloat=false fontsize=6 weight=1 color="#b2a999" tooltip="{d}" labeltooltip="{d}"]\n'
        digraph += "}\n"
    else:
        rootk = ""
        for k in project_inf:
            if root in k:
                rootk = k
                break
        if rootk == "":
            raise ValueError("Root node not found")

        nodes = {}
        par = [project_inf[k]]
        met = {}
        ni = 1
        while len(par) > 0:
            p = par.pop()
            nodes[p["name"]] = { "idx" : ni, "inf": p }
            name = p['name']
            met[name] = 1
            digraph +=f'N{ni} [label="{name}" id="node{ni}" fontsize=8 shape=box color="#b20400" fillcolor="#edd6d5"]\n'
            ni+=1
            for d in p["dependencies"]:
                if d in met: continue
                par.append(project_inf[d])

        for no in nodes:
            inf = nodes[no]["inf"]
            curr = nodes[no]
            curr_idx = curr["idx"]
            dependencies = inf['dependencies']
            for d in dependencies:
                if d not in nodes: continue
                to = nodes[d]
                to_idx = to["idx"]
                digraph +=f'N{curr_idx} -> N{to_idx} [label="" labelfloat=false fontsize=6 weight=1 color="#b2a999" tooltip="{d}" labeltooltip="{d}"]\n'
        digraph += "}\n"

    # print(digraph)

    with open("out.txt", "+w") as f:
        f.write(digraph)

    print(cli_run("dot -Tsvg out.txt > out.svg && open svg.html"))
