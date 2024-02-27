import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, Element

NAMESPACE: str = "{http://maven.apache.org/POM/4.0.0}"


def parse_tree(pom_path: str) -> "ElementTree":
    ET.register_namespace('', "http://maven.apache.org/POM/4.0.0")
    ET.register_namespace('xsi', "http://www.w3.org/2001/XMLSchema-instance")
    return ET.parse(pom_path)


def lookup(root: Element, tag: str) -> Element:
    t = (NAMESPACE + tag) if not tag.startswith(NAMESPACE) else tag
    return root.find(t)


import sys
import pom_parser

alias = {
    "goauth-client" : "goauth",
    "auth-service-api" : "auth-service",
}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Specify where the pom is:")
        sys.exit(0)

    pom = sys.argv[1]

    # print(f"Path to pom: '{pom}'")
    tree = pom_parser.parse_tree(pom)
    root = tree.getroot()
    prop_tag = pom_parser.lookup(root, "properties")

    if prop_tag is None:
        print("project.properties is not found")
        sys.exit()

    properties = []
    for k in prop_tag.iter(): properties.append(k.tag)

    prelen = len(pom_parser.NAMESPACE)
    for i in range(len(properties)): properties[i] = properties[i][prelen:]

    for p in properties:
        if p == "properties": continue
        if p == "java.version": continue
        if p == "api.version": continue

        t = pom_parser.lookup(prop_tag, p)

        name: str = p
        j = name.rfind(".version")
        if j > -1: name = name[:j]
        if name in alias: name = alias[name]

        ver = t.text
        if t is not None: print(f"- [{name} v{ver}](https://github.com/CurtisNewbie/{name}/tree/v{ver})")


