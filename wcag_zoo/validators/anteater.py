from wcag_zoo.utils import WCAGCommand

# https://www.w3.org/TR/WCAG20-TECHS/H37.html
# https://www.w3.org/TR/WCAG20-TECHS/H67.html


class Anteater(WCAGCommand):
    """
    Anteater checks for alt and title attributes in image tags in HTML against the requirements of the WCAG2.0 standard
    """

    animal = """
        Anteaters eat ants and termites. They have long, sharp claws and a long,
        sticky tongue. The tongue can be up to 60 cm long, as long as a person's
        arm. The anteater opens an ant nest with its claws. Then it licks up the
        ants with its tongue.

        - https://simple.wikipedia.org/wiki/Anteater
    """

    xpath = '/html/body//img'

    error_codes = {
        'anteater-1': "Missing alt tag on image for element",
        'anteater-2': "Blank alt tag on image for element",
    }

    def validate_element(self, node):
        if node.get('alt') is None:
            message = (
                u"Missing alt tag on image for element - {xpath}"
                u"\n    Image was: {img_url}"
            ).format(
                xpath=node.getroottree().getpath(node),
                img_url=node.get('src')
            )

            self.add_failure(**{
                'guideline': '1.1.1',
                'technique': 'H37',
                'node': node,
                'message': message,
                'error_code': 'anteater-1'
            })
        elif node.get('alt') == "":
            message = (
                u"Blank alt tag on image for element - {xpath}"
                u"\n    Image was: {img_url}"
                u"\n    Only use blank alt tags when an image is purely decorative."
            ).format(
                xpath=node.getroottree().getpath(node),
                img_url=node.get('src')
            )

            self.add_warning(**{
                'guideline': '1.1.1',
                'technique': 'H37',
                'node': node,
                'message': message,
                'error_code': 'anteater-2'
            })
        else:
            self.add_success(
                guideline='1.1.1',
                technique='H37',
                node=node
            )

if __name__ == "__main__":
    cli = Anteater.as_cli()
    cli()
