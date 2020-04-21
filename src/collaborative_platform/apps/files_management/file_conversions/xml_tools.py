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


def add_property_to_element(parent, property_xpath, value):
    property_xpath = property_xpath.replace('./', '')
    splitted_property_xpath = property_xpath.split('/')

    if len(splitted_property_xpath) > 1:
        child_xpath = '/'.join(splitted_property_xpath[:-1])
        child_xpath = f'./{child_xpath}'

        child = get_first_xpath_match(parent, child_xpath, XML_NAMESPACES)

        if not child:
            create_elements_from_xpath(parent, child_xpath)
            child = get_first_xpath_match(parent, child_xpath, XML_NAMESPACES)

    else:
        child = parent

    property = splitted_property_xpath[-1]

    if '@' in property:
        key = property.replace('@', '')
        child.set(key, value)

    elif 'text()' in property:
        child.text = value

    else:
        raise ValueError("Xpath for this property not pointing to attribute(@) or text (text())")


def create_elements_from_xpath(root, xpath):
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

    child = get_first_xpath_match(root, child_xpath, XML_NAMESPACES)

    if xpath != child_xpath:
        xpath = xpath.replace(child_xpath, '.', 1)
    else:
        xpath = None

    if not child:
        parsed_attributes = {}

        if match_with_attributes:
            attributes_regex = r'\[.*?\]'
            match = re.search(attributes_regex, child_xpath)

            attributes_part = match.group()
            name_part = child_xpath.replace(attributes_part, '')

            attribute_regex = r'@\S*?=[\'"].*?[\'"]'
            attributes = re.findall(attribute_regex, attributes_part)

            for attribute in attributes:
                key = attribute.split('=')[0]
                key = key.replace('@', '')

                value = attribute.split('=')[1]
                value = re.sub(r'[\'"]', '', value)

                parsed_attributes.update({key: value})

        else:
            name_part = child_xpath

        name_part = name_part.replace('./', '')

        if ':' in name_part:
            prefix = name_part.split(':')[0]
            name = name_part.split(':')[1]

        else:
            prefix = ''
            name = name_part

        namespace = '{%s}' % XML_NAMESPACES[prefix]

        child = etree.Element(namespace + name, nsmap=NS_MAP)

        if parsed_attributes:
            for key, value in parsed_attributes.items():
                child.set(key, value)

        root.append(child)

    if xpath:
        return create_elements_from_xpath(child, xpath)
    else:
        return root
