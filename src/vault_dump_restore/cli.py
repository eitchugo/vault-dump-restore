# -*- coding: utf-8 -*-
"""
    vault_dump_restore.cli
    ~~~~~~~~~~~~~~~~~~~~~~~

    This is the CLI interface for running the package.
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import logging
import os
import json
from vault_dump_restore import __version__
from vault_dump_restore.dump import VaultDumpKeys
from vault_dump_restore.restore import VaultRestoreKeys
import hvac

logger = logging.getLogger("vault_dump_restore")

def get_common_arguments():
    """
    Common arguments used by all commands.

    Each item from the list accepts a dict in this format::

        {
            "arg1,arg2": {
                "kwarg1": "value1",
                "kwarg2": "value2"
            }
        }

    Example::

        {
            "-p,--parameter": {
                "help": "This specifies a parameter in the example.",
                "dest": "parameter_var"
            }
        }

    Returns:
            list: A list of dicts containing the arguments to be used by
                method `argparse.ArgumentParser.add_parse()`
    """
    arguments_list = []
    arguments_list.append({
        "-d,--debug": {
            "help": 'Set LOG_LEVEL to DEBUG.',
            "dest": "debug_mode",
            "action": "store_true"
        }
    })

    arguments_list.append({
        "--address": {
            "help": f"Address of the Vault server. This can also be specified "
                f"via the VAULT_ADDR environment variable. "
                f"Defaults to https://127.0.0.1:8200",
            "dest": "vault_addr",
            "default": "https://127.0.0.1:8200"
        }
    })

    arguments_list.append({
        "--show-log-dates": {
            "help": 'Show log dates and severity on each message',
            "dest": "show_log_dates",
            "action": "store_true"
        }
    })

    arguments_list.append({
        "-p,--path": {
            "help": "Path to work on. This includes the secrets engine."
                "Example: secrets/subdir'. Defaults to /.",
            "dest": "path",
            "default": "/"
        }
    })

    return arguments_list

def common_setup(argument_parser):
    """
    Common checks and initial setup used by all commands

    Args:
        argument_parser: The parsed arguments returned from method
            `argparse.ArgumentParser.parse_args()`

    Returns:
        int: The status from the setup. 0 if everything went OK, >1 if not.
    """
    # logging setup
    if not logging.getLogger().hasHandlers():
        if argument_parser.show_log_dates:
            logformat='[%(asctime)s] [%(levelname)s] %(message)s'
        else:
            logformat='%(message)s'

        logging.basicConfig(format=logformat)

    logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "FATAL"))

    # logging settings - environment variables are always a priority
    if argument_parser.debug_mode:
        logger.setLevel("DEBUG")
        logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "DEBUG"))
    else:
        # defaults to info
        logger.setLevel("INFO")
        logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO"))

    # required environment variables check
    env_vars = os.environ.copy()
    if not "VAULT_TOKEN" in env_vars:
        logger.error("Error while reading environment variable VAULT_TOKEN. You need a valid/authenticated token.")
        return 1

    if not "VAULT_ADDR" in env_vars:
        os.environ["VAULT_ADDR"] = argument_parser.vault_addr

    # ensure utf-8 encoding
    os.environ["PYTHONIOENCODING"] = "utf-8"

    # vault authorization check
    hvac_client = hvac.Client(
        url=os.getenv("VAULT_ADDR"),
        token=os.getenv('VAULT_TOKEN')
    )

    if not hvac_client.is_authenticated():
        logger.error("Error while using the vault server using the token. Check its address and token.")
        return 1

    return 0

def dump():
    """
    Dump commnad called by CLI

    Returns:
        int: The status from the program. 0 if everything went OK, >1 if not.
    """
    # command argument parser
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=(
            f"vault-dump {__version__}{os.linesep}"
            "Dumps keys from a Hashicorp Vault instance into a file"
        )
    )

    # load common arguments into the parser
    common_args = get_common_arguments()
    for argument in common_args:
        for args, kwargs in argument.items():
            args = args.split(",")
            parser.add_argument(*args, **kwargs)

    # dump options
    parser.add_argument(
        '-m',
        '--mask',
        help='All secrets in the dump will be hidden/masked.',
        dest="secrets_mask",
        action='store_true'
    )

    parser.add_argument(
        '-o',
        '--output',
        help='Choose output format. Could be: (json|vault). Defaults to vault.',
        dest="output",
        default='vault'
    )

    parser.add_argument(
        '-t',
        '--type',
        help='Dump a certain type of secret engine. Currently supports: secrets, transit. Defaults to secrets.',
        dest="type",
        default='secrets'
    )    

    # parse the arguments, show in the screen if needed
    parser = parser.parse_args()

    # common setup
    setup_status = common_setup(parser)
    if setup_status > 0:
        return setup_status

    # check if output format is valid
    if not parser.output == "json" and not parser.output == "vault":
        logger.error(f"Invalid output format {parser.output}")

    # check if secrets engine type is valid
    if not parser.type == "secrets" and not parser.type == "transit":
        logger.error(f"Invalid secrets engine type {parser.type}")

    dump = VaultDumpKeys(
        os.getenv("VAULT_ADDR"),
        os.getenv("VAULT_TOKEN"),
    )

    if parser.type == "secrets":
        secrets_dump = dump.dump_kv(parser.path, parser.secrets_mask)
    elif parser.type == "transit":
        secrets_dump = dump.dump_transit(parser.path, parser.secrets_mask)

    # JSON output
    if parser.output == "json":
        print(dump.dump_to_json(secrets_dump, 2))

    # Vault client commands output
    elif parser.output == "vault" and parser.type == "secrets":
        path_prefix = parser.path.lstrip("/")
        commands_dump = dump.dump_kv_to_vault(secrets_dump, path_prefix)
        for command in commands_dump:
            print(command)

    elif parser.output == "vault" and parser.type == "transit":
        commands_dump = dump.dump_transit_to_vault(secrets_dump)
        for command in commands_dump:
            print(command)

    return 0

def restore():
    """
    Restore command called by CLI

    Returns:
        int: The status from the program. 0 if everything went OK, >1 if not.
    """
    # command argument parser
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=(
            f"vault-restore {__version__}{os.linesep}"
            "Restores keys from a file into a Hashicorp Vault instance"
        )
    )

    # load common arguments into the parser
    common_args = get_common_arguments()
    for argument in common_args:
        for args, kwargs in argument.items():
            args = args.split(",")
            parser.add_argument(*args, **kwargs)

    # restore options
    parser.add_argument('file', type=str,
        help='JSON file with the secrets')

    # parse the arguments, show in the screen if needed
    parser = parser.parse_args()

    # common setup
    setup_status = common_setup(parser)
    if setup_status > 0:
        return setup_status

    restore = VaultRestoreKeys(
        os.getenv("VAULT_ADDR"),
        os.getenv("VAULT_TOKEN"),
    )

    print("Command not implemented yet. Try the vault output and run a restore as a shell script.")

    return 0
