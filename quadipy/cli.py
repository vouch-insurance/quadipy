import os

import click

from quadipy.schemas.graph_format_config import GraphFormatConfig

OK_GREEN = "\033[92m"
OK_MARK = "\u2713"
ERROR_RED = "\033[91m"
END_COLOR = "\033[0m"


def validate_single_config(single_config_path: str) -> None:
    try:
        GraphFormatConfig.parse_file(single_config_path)
        click.echo(f"* {single_config_path} ... {OK_GREEN + OK_MARK + END_COLOR}")
    except Exception as e:
        click.echo(f"* {single_config_path} ... {ERROR_RED + str(e) + END_COLOR}")


def validate_configs(config_dir: str) -> None:
    for root, _, files in os.walk(config_dir):
        for name in files:
            single_config_path = os.path.join(root, name)
            validate_single_config(single_config_path)


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def validate(path: str) -> None:
    """
    validate the config file(s) by path

    path could be a directory e.g. examples
    or a single config file e.g. examples/simple.json
    """
    if os.path.isdir(path):
        validate_configs(path)
    else:
        validate_single_config(path)


if __name__ == "__main__":
    cli()
