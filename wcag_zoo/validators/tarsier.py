from wcag_zoo.utils import WCAGCommand


class Tarsier(WCAGCommand):
    """
    Tarsier reads heading levels in HTML documents (H1,H2,...) to verify the order and completion
    of headings against the requirements of the WCAG2.0 standard.
    """

    animal = """
        The tarsiers are prosimian (non-monkey) primates. They got their name
        from the long bones in their feet.
        They are now placed in the suborder Haplorhini, together with the
        simians (monkeys).

        Tarsiers have huge eyes and long feet, and catch the insects by jumping at them.
        During the night they wait quietly, listening for the sound of an insect moving nearby.

        - https://simple.wikipedia.org/wiki/Tarsier
    """

    xpath = '/html/body//*[%s]' % (" or ".join(['self::h%d' % x for x in range(1, 7)]))

    error_codes = {
        'tarsier-1': "Incorrect header found at {elem} - H{bad} should be H{good}, text in header was {text}",
        'tarsier-2-warning': "{not_h1} header seen before the first H1. Text in header was {text}",
    }

    def run_validation_loop(self, xpath=None, validator=None):
        if xpath is None:
            xpath = self.xpath
        headers = []
        for node in self.tree.xpath(xpath):
            if self.check_skip_element(node):
                continue
            depth = int(node.tag[1])
            headers.append(depth)
        depth = 0
        for node in self.tree.xpath(xpath):
            h = int(node.tag[1])
            if h == depth:
                self.add_success(
                    guideline='1.3.1',
                    technique='H42',
                    node=node
                )
            elif h == depth + 1:
                self.add_success(
                    guideline='1.3.1',
                    technique='H42',
                    node=node
                )
            elif h < depth:
                self.add_success(
                    guideline='1.3.1',
                    technique='H42',
                    node=node
                )
            elif depth == 0:
                if h != 1:
                    self.add_warning(
                        guideline='1.3.1',
                        technique='H42',
                        node=node,
                        message=Tarsier.error_codes['tarsier-2-warning'].format(
                            not_h1=node.tag, text=node.text,
                        ),
                        error_code='tarsier-2-warning'
                    )
                else:
                    self.add_success(
                        guideline='1.3.1',
                        technique='H42',
                        node=node
                    )
            else:
                self.add_failure(
                    guideline='1.3.1',
                    technique='H42',
                    node=node,
                    message=Tarsier.error_codes['tarsier-1'].format(
                        elem=node.getroottree().getpath(node),
                        good=depth + 1,
                        bad=h,
                        text=node.text
                    ),
                    error_code='tarsier-1'
                )
            depth = h

if __name__ == "__main__":
    cli = Tarsier.as_cli()
    cli()
