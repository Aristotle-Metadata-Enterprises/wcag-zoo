import os
import click
from wcag_zoo.utils import WCAGCommand, get_wcag_class


class Parade(WCAGCommand):
    """
    Run a number of validators together across a file or collection of files in a single command.
    """

    def __init__(self, *args, **kwargs):
        self.exclude_validators = list(kwargs.pop('exclude_validators', []))
        super(Parade, self).__init__(*args, **kwargs)

    def validate_document(self, html):
        self.tree = self.get_tree(html)
        rv = sorted([
            filename[:-3]
            for filename in os.listdir(os.path.dirname(__file__))
            if (
                filename.endswith('.py') and
                not filename.startswith('_') and
                not filename.startswith('.') and
                filename[:-3] not in ['parade'] + self.exclude_validators
            )
        ])

        total_results = {
            "success": self.success,
            "failures": self.failures,
            "warnings": self.warnings,
            "skipped": self.skipped
        }

        for validator_name in rv:
            cmd = get_wcag_class(validator_name)
            instance = cmd(**self.kwargs)
            instance._tree = self.tree
            results = instance.validate_document(html)
            for k, v in results.items():
                total_results[k].update(v)
        return total_results

    @classmethod
    def as_cli(cls):
        """
        Exposes the WCAG validator as a click-based command line interface tool.
        """
        return click.option(
            '--exclude_validators', '-E', multiple=True, type=str, help='Repeatable argument to prevent certain validators from being run'
        )(super(Parade, cls).as_cli())

if __name__ == "__main__":
    cli = Parade.as_cli()
    cli()
