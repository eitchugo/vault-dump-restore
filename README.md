# vault-dump-restore

Dumps keys from a Hashicorp instance into a file, to be able to restore it later
in any other instance. Remember to encrypt the file!

This only supports reading a kv2 engine. Also note that these dumps and
restores are meant to be used very rarely and under emergency situations
since this kind of defeats the purpose of having a vault (storing secrets
inside a vault, sealed with a key, etc) - you're dumping all the secrets
to a external file!

The following examples use gpg commands to encrypt/decrypt the files.

Example for dump:

```bash
# make sure you have the vault environment variables:
export VAULT_ADDR=https://<vault-addr>
export VAULT_TOKEN=<vault-token>

# dumps the entire vault kv secrets in a shell script (vault commands)
vault-dump -o vault vault -o | gpg --symmetric --cipher-algo AES256 > vault-backup.sh.enc

# dumps a specific path with the default json format
vault-dump -p secrets/specific-app | gpg --symmetric --cipher-algo AES256 > vault-backup.json.enc
```

Examples for restore:

```bash
# make sure you have the vault environment variables:
export VAULT_ADDR=https://<vault-addr>
export VAULT_TOKEN=<vault-token>

# you will also must have the secret engine created
vault secrets enable -path=secrets kv

# restore a full dump using the shell script format
. <(gpg -qd vault-backup.sh.enc)

# restore a full dump using the JSON format
gpg -qd vault-backup.json.enc | vault-restore -

# restore a specific path using the JSON format
gpg -qd vault-backup.json.enc | vault-restore -p secrets/specific-app -
```

## Installation and usage

Installation can be done through pip:

```bash
pip install vault-dump-restore
```

Use the `-h` parameter to get help from the commands:

```bash
vault-dump -h
vault-restore -h
```

## Contents

* [API Reference](api_ref.md)
* [ChangeLog](changelog.md)

## Setup and usage for local development

Make a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

Note that this will also install the local dependencies, which might change after
some time. If needed, you can run `pip install -e .` again to reinstall the
updated dependencies anytime.

## Documentation build

Run:

```bash
make docs
```

HTML documentation will be generated at `docs/_build/html`.
