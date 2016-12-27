import click
from wcag_zoo.utils import print_if, common_cli, common_wcag, get_tree, build_msg, WCAGCommand

error_codes = {
    1: "Duplicate `accesskey` attribute '{key}' found. First seen at element {elem}",
    2: "Blank `accesskey` attribute found at element {elem}",
    3: "No `accesskey` attributes found, consider adding some to improve keyboard accessibility",
}

@common_wcag(animal="""The aye-aye is a lemur which lives in rain forests of Madagascar, a large island off the southeast coast of Africa.
The aye-aye has rodent-like teeth and a special thin middle finger to get at the insect grubs under tree bark.

- https://simple.wikipedia.org/wiki/Aye-aye""")
def ayeaye(html, level="AA", verbosity=1, **kwargs):
    """
    Checks for the existance of access key attributes within a HTML document and confirms their uniqueness.
    Fails if any duplicate access keys are found in the document
    Warns if no access keys are found in the document
    """

    tree = get_tree(html)
    
    success = 0
    failed=0
    failures = []
    warnings = []
    skipped = []

    # find all nodes that have access keys
    access_key_elems = tree.xpath('/html/body//*[@accesskey]')
    found_keys = {}
    for node in access_key_elems:
        access_key = node.get('accesskey')
        if not access_key:
            # Blank or empty
            failures.append(build_msg(
                guideline = '2.1.1',
                technique = 'G20',
                node = node,
                message =  error_codes[2].format(elem=tree.getpath(node)),
            ))
        elif access_key not in found_keys.keys():
            success += 1
            found_keys[access_key] = tree.getpath(node)
        else:
            failures.append(build_msg(
                guideline = '2.1.1',
                technique = 'G20',
                node = node,
                message =  error_codes[1].format(key=access_key,elem=found_keys[access_key]),
            ))

    if len(access_key_elems) == 0:
        warnings.append(build_msg(
            guideline = '2.1.1',
            technique = 'G20',
            node = tree.xpath('/html/body')[0],
            message =  error_codes[3]
        ))

    return {
        "success": success,
        "failures": failures,
        "warnings": warnings,
        "skipped": skipped
    }

class Ayeaye(WCAGCommand):
    """
    Checks for the existance of access key attributes within a HTML document and confirms their uniqueness.
    Fails if any duplicate access keys are found in the document
    Warns if no access keys are found in the document
    """

    animal = """
        The aye-aye is a lemur which lives in rain forests of Madagascar, a large island off the southeast coast of Africa.
        The aye-aye has rodent-like teeth and a special thin middle finger to get at the insect grubs under tree bark.

        - https://simple.wikipedia.org/wiki/Aye-aye
    """
    xpath = '/html/body//*[@accesskey]'
    error_codes = {
        1: "Duplicate `accesskey` attribute '{key}' found. First seen at element {elem}",
        2: "Blank `accesskey` attribute found at element {elem}",
        3: "No `accesskey` attributes found, consider adding some to improve keyboard accessibility",
    }

    def validate_document(self, html):
        self.tree = self.get_tree(html)

        # find all nodes that have access keys
        self.found_keys = {}
        iterations = self.run_validation_loop()
        if len(self.tree.xpath('/html/body//*[@accesskey]')) == 0:
            self.add_warning(
                guideline = '2.1.1',
                technique = 'G20',
                node = self.tree.xpath('/html/body')[0],
                message =  Ayeaye.error_codes[3]
            )

        return {
            "success": self.success,
            "failures": self.failures,
            "warnings": self.warnings,
            "skipped": self.skipped
        }

    def validate_element(self, node):
        access_key = node.get('accesskey')
        if not access_key:
            # Blank or empty
            self.add_failure(
                guideline = '2.1.1',
                technique = 'G20',
                node = node,
                message =  Ayeaye.error_codes[2].format(elem=node.getroottree().getpath(node)),
            )
        elif access_key not in self.found_keys.keys():
            self.success += 1
            self.found_keys[access_key] = node.getroottree().getpath(node)
        else:
            self.add_failure(
                guideline = '2.1.1',
                technique = 'G20',
                node = node,
                message =  Ayeaye.error_codes[1].format(key=access_key,elem=self.found_keys[access_key]),
            )

if __name__ == "__main__":
    cli = Ayeaye.as_cli()
    cli()
