from wcag_zoo.utils import WCAGCommand

# https://www.w3.org/TR/WCAG20-TECHS/G149.html
# https://www.w3.org/TR/UNDERSTANDING-WCAG20/navigation-mechanisms-focus-visible.html


class Glowworm(WCAGCommand):
    """
    Glowworm checks for supressed focus outlines.
    """

    animal = """
        A glow-worm, or glowworm, is an insect. Other names for glow-worms are
        fire-fly and lightning bug.

        There are several insects given this name. Most are beetles, but one is
        a fly, Arachnocampa. They are nocturnal, active during the night.
        They have special organs that can produce light. This is used to find
        mates. The patterns in which the beetles flash is unique per species.

        - https://simple.wikipedia.org/wiki/Glow-worm
    """

    xpath = '/html/body//*'

    error_codes = {
        'glowworm-1': "ELement focus hidden without alternate styling",
    }
    premolar_kwargs = {
        "exclude_pseudoclasses": False
    }

    def skip_element(self, node):
        if node.tag in ['script', 'style']:
            return True

    def validate_element(self, node):
        style = node.get('style', "")

        if ":focus{outline:none}" in style or style.startswith("focus{outline:none}"):
            message = (
                u"Input or element has suppressed focus styling - {xpath}"
            ).format(
                xpath=node.getroottree().getpath(node),
            )

            self.add_failure(**{
                'guideline': '2.4.5',
                'technique': 'G149',
                'node': node,
                'message': message,
                'error_code': 'glowworm-1'
            })
        else:
            self.add_success(
                guideline='2.4.7',
                technique='G149',
                node=node
            )

if __name__ == "__main__":
    cli = Glowworm.as_cli()
    cli()
