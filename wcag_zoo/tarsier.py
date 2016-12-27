from lxml import etree
import click
from wcag_zoo.utils import WCAGCommand

class Tarsier(WCAGCommand):
    """
    Tarsier reads heading levels in HTML documents (H1,H2,...H6) to verfiy order and completion against the requirements of the WCAG2.0 standard
    """

    animal = """
        The tarsiers are prosimian (non-monkey) primates. They got their name from the long bones in their feet.
        They are now placed in the suborder Haplorhini, together with the simians (monkeys).

        Tarsiers have huge eyes and long feet, and catch the insects by jumping at them.
        During the night they wait quietly, listening for the sound of an insect moving nearby.
        
        - https://simple.wikipedia.org/wiki/Tarsier
    """

    xpath = '/html/body//*[%s]'%(" or ".join(['self::h%d'%x for x in range(7)]))

    error_codes = {
        1: "Duplicate `accesskey` attribute '{key}' found. First seen at element {elem}",
    }

    def validate_element(self, node):
        print(node.tag, node.text)

if __name__ == "__main__":
    cli = Tarsier.as_cli()
    cli()