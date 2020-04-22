import re

from lxml import etree

from collaborative_platform.settings import NS_MAP, XML_NAMESPACES


def get_first_xpath_match(root, xpath, namespaces):
    matches = root.xpath(xpath, namespaces=namespaces)

    if matches:
        match = matches[0]

        return match
    else:
        return None


def add_property_to_element(root, property_xpath, value):
    target_element_xpath = '/'.join(property_xpath.split('/')[:-1]) or '.'
    target_property = property_xpath.split('/')[-1]

    target_element = get_first_xpath_match(root, target_element_xpath, XML_NAMESPACES)

    if target_element is None:
        create_elements_from_xpath(root, target_element_xpath, XML_NAMESPACES)
        target_element = get_first_xpath_match(root, target_element_xpath, XML_NAMESPACES)

    if '@' in target_property:
        key = target_property.replace('@', '')
        target_element.set(key, value)

    elif 'text()' in target_property:
        target_element.text = value

    else:
        raise ValueError("Xpath for this property not pointing to attribute(@) or text (text())")


def get_or_create_element_from_xpath(root, xpath, namespaces):
    element = get_first_xpath_match(root, xpath, namespaces)

    if not element:
        create_elements_from_xpath(root, xpath, namespaces)
        element = get_first_xpath_match(root, xpath, namespaces)

    return element


def create_elements_from_xpath(root, xpath, namespaces):
    if xpath == '.':
        return

    child_xpath = __get_child_xpath(xpath)
    child = get_first_xpath_match(root, child_xpath, namespaces)

    if child is None:
        child = __create_child_element(child_xpath)

        root.append(child)

    xpath = xpath.replace(child_xpath, '.', 1)

    return create_elements_from_xpath(child, xpath, namespaces)


def __get_child_xpath(xpath):
    """Function created to properly handle splitting xpath with URLs in elements attributes"""

    element_with_attributes_regex = r'^\.\/[^\/]+\[.+?]'
    element_without_attributes_regex = r'^\.\/[^\[\]\/]+'

    match_with_attributes = re.search(element_with_attributes_regex, xpath)
    match_without_attributes = re.search(element_without_attributes_regex, xpath)

    if match_with_attributes:
        child_xpath = match_with_attributes.group()

    elif match_without_attributes:
        child_xpath = match_without_attributes.group()

    else:
        raise ValueError(f"Xpath to element is incorrect: {xpath}")

    return child_xpath


def __create_child_element(child_xpath):
    name = __get_element_name(child_xpath)
    attributes = __get_element_attributes(child_xpath)

    if ':' in name:
        prefix = name.split(':')[0]
        name = name.split(':')[1]
        namespace = '{%s}' % XML_NAMESPACES[prefix]
        name = namespace + name

    child = etree.Element(name, nsmap=NS_MAP)

    if attributes:
        for key, value in attributes.items():
            child.set(key, value)

    return child


def __get_element_name(child_xpath):
    name = child_xpath.replace('./', '')
    name = name.split('[')[0]

    return name


def __get_element_attributes(child_xpath):
    attributes_regex = r'\[.*?\]'
    match = re.search(attributes_regex, child_xpath)

    attributes = {}

    if match:
        attributes_part = match.group()
        attributes = __parse_attributes(attributes_part)

    return attributes


def __parse_attributes(attributes_part):
    parsed_attributes = {}

    attribute_regex = r'@\S*?=[\'"].*?[\'"]'
    attributes = re.findall(attribute_regex, attributes_part)

    for attribute in attributes:
        key = attribute.split('=')[0]
        key = key.replace('@', '')

        value = attribute.split('=')[1]
        value = re.sub(r'[\'"]', '', value)

        parsed_attributes.update({key: value})

    return parsed_attributes
