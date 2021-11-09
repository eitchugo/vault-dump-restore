# -*- coding: utf-8 -*-
"""
    vault_dump_restore.restore
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Restore methods
"""
import os
import json
import hvac

class VaultRestoreKeys:
    """
    Represents a keys restore to a vault instance
    """
    def __init__(self, hvac_url, hvac_token, skip_tls=False):
        """
        Creates a new restore object

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

    def restore(self, path):
        """
        Dumps a path recursively with all keys and values.

        Args:
            path (str): Path to look for keys.

        Returns:
            dict: all keys and values from the path
        """
        return {}