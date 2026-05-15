# Local Portage Overlay

This directory contains a small local overlay for installing this Python 3.12
Porthole build with Portage.

## Build the local distfile

From the repository root:

```sh
./packaging/portage/make-local-distfile.sh
```

This creates:

```text
/var/cache/distfiles/porthole-20260515.tar.gz
```

If you do not run the script as root, it writes the tarball to
`/tmp/porthole-distfiles` and prints the command to copy it into place.

## Add the overlay to Portage

Copy the example repo config:

```sh
sudo install -Dm0644 packaging/portage/repos.conf/porthole-local.conf \
    /etc/portage/repos.conf/porthole-local.conf
```

Or add the same content manually and adjust `location` if your checkout lives
somewhere else:

```ini
[porthole-local]
location = /home/user/projects/porthole/porthole-py3/packaging/portage/overlay
masters = gentoo
auto-sync = no
```

Then create/update the Manifest and install:

```sh
cd packaging/portage/overlay/app-portage/porthole
ebuild porthole-20260515-r1.ebuild manifest
sudo emerge -av app-portage/porthole
```

If Portage reports that `python_targets_python3_12` is missing, install the
package.use example:

```sh
sudo install -Dm0644 packaging/portage/package.use/porthole \
    /etc/portage/package.use/porthole
```

