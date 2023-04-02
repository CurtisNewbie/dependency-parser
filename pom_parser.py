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

