# -*- coding: utf-8 -*-
"""
    vault_dump_restore.dump
    ~~~~~~~~~~~~~~~~~~~~~~~

    Dump methods
"""
import os
import json
import hvac

class VaultDumpKeys:
    """
    Represents a keys dump from a vault instance
    """
    def __init__(self, hvac_url, hvac_token, skip_tls=False):
        """
        Creates a new dump object

        Args:
            hvac_url (str): Vault server to connect to
            hvac_token (str): Authentication token to be used when connecting
                to vault
            skip_tls (bool): Wheter to check for certificate or not while using
                HTTPS
        """
        self.hvac_client = hvac.Client(
            url=os.getenv(hvac_url),
            token=hvac_token
        )
        self._sentinel = object()

    def dump(self, path, mask=False, root=False):
        """
        Dumps a path recursively with all keys and values.

        Args:
            path (str): Path to look for keys.
            mask (bool): If True, all secrets will be hidden in the values.
                Defaults to False.
            root (bool): If True, we treat the tree as the root of an engine,
                which uses a list and not a get.

        Returns:
            dict: all keys and values from the path
        """

        results = {}

        # when dumping the root
        if path == "/":
            # returns a list of secret engines
            engines = self.hvac_client.sys.list_mounted_secrets_engines()['data']
            for engine, values in engines.items():
                # we only accept KV2 engine types
                try:
                    if not values['type'] == "kv":
                        continue
                    elif values['options'] and not values['options']['version'] == "2":
                        continue
                except KeyError:
                    continue

                results[engine] = self.dump(path=engine, mask=mask, root=True)
        else:
            # split into the secret engine name and the actual secret path
            path_args = path.split("/")
            if root == True:
                # the root list of a secret engine
                path = "/"
                mount_point = path_args[0]
            else:
                # a sub-path of a secret engine
                path = "/".join(path_args[1:])
                mount_point = path_args[0]

            if path.endswith("/"):
                # this is a path, not a secret
                try:
                    listing = self.hvac_client.secrets.kv.v2.list_secrets(
                        path=path,
                        mount_point=mount_point
                    )['data']['keys']
                except hvac.exceptions.InvalidPath:
                    # we ignore empty paths
                    return results

                # recursively list keys within this path
                for key in listing:
                    results[key] = self.dump(path=f"{mount_point}/{path}{key}", mask=mask)
            else:
                # this is a secret, we read it
                try:
                    results = self.hvac_client.secrets.kv.v2.read_secret_version(
                        path=path,
                        mount_point=mount_point
                    )['data']['data']
                except hvac.exceptions.InvalidPath:
                    # we ignore destroyed secrets
                    return results

                # mask: we replace all values to a hidden value
                if mask:
                    for key in results:
                        results[key] = "<hidden>"

        return results

    def dump_to_json(self, dump, indent=2):
        """
        Transforms a dump into a JSON formatted output

        Args:
            dump (dict): Secrets dump to transform. This can be
                generated using the method dump.
            indent (int|Optional): Indentation to use on outputting
                the JSON. This parameter is passed to the json.dumps() method.
                None disables the pretty format.

        Returns:
            str: A JSON string with the dump contents.
        """
        return json.dumps(dump, indent=indent)

    def dump_to_vault(self, dump, path_prefix=""):
        """
        Transforms a dump into a series of vault client commands
        
        Args:
            dump (dict): Secrets dump to transform. This can be
                generated using the method dump.
            path_prefix (str|Optional): Prefix to be used before all lines.
                Defaults to an empty string.

        Returns:
            list: One command per item
        """
        # add trailing slash to path_prefix if needed
        if not path_prefix.endswith("/"):
            path_prefix = f"{path_prefix}/"

        lines = []
        old_key_path = None
        new_line = ""
        command_paths = self.dict_to_path(dump) 
        for is_last, dict_item in self._iter_check_last(command_paths):
            path, value = dict_item

            # separate key path from key itself
            key_path = "".join(path[:-1])
            key = path[-1]

            # add quotes if needed
            key = self._quotify_single(str(key))
            value = self._quotify_single(str(value))

            if key_path == old_key_path:
                # reuse the same key_path
                new_line = f"{new_line} '{key}'='{value}'"
            
            else:
                # first element is always new
                if not old_key_path:
                    new_line = f"{key_path}' '{key}'='{value}'"
                else:
                    # add the last line to the list
                    lines.append(f"vault kv put '{path_prefix}{new_line}")

                    # init a new key_path
                    new_line = f"{key_path}' '{key}'='{value}'"

            # last element
            if is_last:
                lines.append(f"vault kv put '{path_prefix}{new_line}")

            old_key_path = key_path

        return lines

    def dict_to_path(self, dictionary, path=None):
        """
        Transforms a dictionary's full path into one string. Means to be
        used recursivelly.

        Args:
            dictionary (dict): The dictionary itself
            path (str): Current path of the dictionary to traverse into
        """
        if path is None:
            path = []

        for key, value in dictionary.items():
            newpath = path + [key]

            if isinstance(value, dict):
                for u in self.dict_to_path(value, newpath):
                    yield u
            else:
                yield newpath, value

    def _iter_check_last(self, iterable):
        """
        Generator method that determines if an item is the last one during
        an iteration. Took from stackoverflow question 1630320, response
        by jsbueno.

        Args:
            iterable (mixed): An iterable object

        Yields:
            bool, item: True or False if it's the last item of the
                iterable, then the item from the iterable.
        """
        iterable = iter(iterable)
        current_element = next(iterable, self._sentinel)
        while current_element is not self._sentinel:
            next_element = next(iterable, self._sentinel)
            yield (next_element is self._sentinel, current_element)
            current_element = next_element

    def _quotify_single(self, string):
        """
        Adds bash quotes around a single quote. This is useful when a key
        or secret has the single quote character ('), which should be
        escaped.

        For example::
            mytesting'123 turns into: mytesting'"'"'123

        Args:
            string (str): String to be escaped

        Returns:
            string: Escaped string
        """
        return string.replace("'", "'\"'\"'")
