# ChangeLog for vault-dump-restore

Here you can see a full list of changes between each release.

## 0.5.1

Released on Mar 27th, 2022

* Fixed transit dump when a engine has no keys

## 0.5.0

Released on Mar 26th, 2022

* Added support for backing up transit keys and their respective engines
* Added "-t" parameter to specify which engine type (secrets or transit)
* Output now defaults to vault since the json method is still not completed

## 0.4.3

Released on Jan 20th, 2022

* On vault client command output, when the value begins with '@',
  the vault client assumes it's a file reference, so we escape it
  on the ouput.

## 0.4.2

Released on Jan 18th, 2022

* Now forcing passing strings to `quotify` method since it uses the
  `str.replace` method.

## 0.4.1

Released on Jan 17th, 2022

* Fixed single quote shell escapes on vault command output
* Minimum python version is 3.6 instead of 3.8

## 0.4.0

Released on Oct 28th, 2021

* Initial release, still on alpha
