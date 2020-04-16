def get_first_xpath_match(root, xpath, namespaces):
    matches = root.xpath(xpath, namespaces=namespaces)

    if matches:
        match = matches[0]

        return match
    else:
        return None
