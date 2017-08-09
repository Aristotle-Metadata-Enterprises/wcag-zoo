from wcag_zoo.utils import WCAGCommand

error_codes = {
    1: "Duplicate `accesskey` attribute '{key}' found. First seen at element {elem}",
    2: "Blank `accesskey` attribute found at element {elem}",
    3: "No `accesskey` attributes found, consider adding some to improve keyboard accessibility",
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
        'ayeaye-1': "Duplicate `accesskey` attribute '{key}' found. First seen at element {elem}",
        'ayeaye-2': "Blank `accesskey` attribute found at element {elem}",
        'ayeaye-3-warning': "No `accesskey` attributes found, consider adding some to improve keyboard accessibility",
    }

    def validate_document(self, html):
        self.tree = self.get_tree(html)

        # find all nodes that have access keys
        self.found_keys = {}
        self.run_validation_loop()
        if len(self.tree.xpath('/html/body//*[@accesskey]')) == 0:
            self.add_warning(
                guideline='2.1.1',
                technique='G202',
                node=self.tree.xpath('/html/body')[0],
                message=Ayeaye.error_codes['ayeaye-3-warning'],
                error_code='ayeaye-3-warning',
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
                guideline='2.1.1',
                technique='G202',
                node=node,
                error_code='ayeaye-2',
                message=Ayeaye.error_codes['ayeaye-2'].format(elem=node.getroottree().getpath(node)),
            )
        elif access_key not in self.found_keys.keys():
            self.add_success(
                guideline='2.1.1',
                technique='G202',
                node=node
            )
            self.found_keys[access_key] = node.getroottree().getpath(node)
        else:
            self.add_failure(
                guideline='2.1.1',
                technique='G202',
                node=node,
                error_code='ayeaye-1',
                message=Ayeaye.error_codes['ayeaye-1'].format(key=access_key, elem=self.found_keys[access_key]),
            )

if __name__ == "__main__":
    cli = Ayeaye.as_cli()
    cli()
