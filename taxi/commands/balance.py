import click

from .base import cli, populate_backends
from ..backends.registry import backends_registry


@cli.command(short_help="Show your current balance.")
@click.pass_context
def balance(ctx):
    populate_backends(ctx.obj['settings'].get_backends())

    for backend_name, backend_uri in ctx.obj['settings'].get_backends():
        backend = backends_registry[backend_name]
        balance = backend.get_balance()

        ctx.obj['view'].show_balance(balance)
