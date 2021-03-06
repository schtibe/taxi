from __future__ import unicode_literals

import click

from ..aliases import aliases_database, Mapping
from ..projects import Project
from .base import cli


@cli.group(invoke_without_command=True)
@click.pass_context
def alias(ctx):
    """
    List or manage aliases.

    If invoked without any subcommand, it will display all your defined
    aliases.
    """
    if ctx.invoked_subcommand is None:
        ctx.forward(list_)


@alias.command(name='list')
@click.argument('search_string', required=False)
@click.option('--reverse', '-r', default=False, is_flag=True,
              help="If this flag is set, list (and search) mappings instead "
                   "of aliases.")
@click.option('--backend', '-b', help="Limit search to given backend.")
@click.pass_context
def list_(ctx, search_string, reverse, backend):
    """
    List configured aliases.
    """
    if not reverse:
        list_aliases(ctx, search_string, backend)
    else:
        show_mapping(ctx, search_string, backend)


@alias.command()
@click.argument('alias', required=True)
@click.argument('mapping', required=True)
@click.option('--backend', '-b', help="Add alias to given backend.")
@click.pass_context
def add(ctx, alias, mapping, backend):
    """
    Add a new alias to your configuration file.
    """
    if not backend:
        backends_list = ctx.obj['settings'].get_backends()
        if len(backends_list) > 1:
            raise click.UsageError(
                "You're using more than 1 backend. Please set the backend to "
                "add the alias to with the --backend option (choices are %s)" %
                ", ".join(dict(backends_list).keys())
            )

    add_mapping(ctx, alias, mapping, backend)


def add_mapping(ctx, alias, mapping, backend):
    if mapping:
        mapping = Project.str_to_tuple(mapping)
        if mapping is None:
            raise click.UsageError(
                "The mapping must be in the format xxx/yyy"
            )
    else:
        mapping = None

    mapping = Mapping(mapping=mapping, backend=backend)

    if alias in aliases_database:
        existing_mapping = aliases_database[alias]
        confirm = ctx.obj['view'].overwrite_alias(
            alias, existing_mapping, False
        )

        if not confirm:
            return

    ctx.obj['settings'].add_alias(alias, mapping)
    ctx.obj['settings'].write_config()

    ctx.obj['view'].alias_added(alias, mapping.mapping)


def show_mapping(ctx, mapping_str, backend):
    mapping = Project.str_to_tuple(mapping_str)

    if mapping is None:
        return

    for alias, m in aliases_database.filter_from_mapping(mapping, backend).items():
        ctx.obj['view'].mapping_detail(
            (alias, m),
            ctx.obj['projects_db'].get(m.mapping[0], m.backend)
            if m.mapping is not None else None
        )


def list_aliases(ctx, search, backend):
    for alias, m in aliases_database.filter_from_alias(search, backend).items():
        ctx.obj['view'].alias_detail(
            (alias, m),
            ctx.obj['projects_db'].get(m.mapping[0], m.backend)
            if m.mapping is not None else None
        )
