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

Install the package.use example:

```sh
sudo install -Dm0644 packaging/portage/package.use/porthole \
    /etc/portage/package.use/porthole
```

Create/update the Manifest from the same distfile that Portage will use, then
install:

```sh
cd packaging/portage/overlay/app-portage/porthole
DISTDIR=/var/cache/distfiles ebuild --force porthole-20260515-r1.ebuild manifest
sudo emerge -av app-portage/porthole
```

If you generated the distfile as a normal user, copy it first and then refresh
the Manifest:

```sh
sudo install -Dm0644 /tmp/porthole-distfiles/porthole-20260515.tar.gz \
    /var/cache/distfiles/porthole-20260515.tar.gz
cd packaging/portage/overlay/app-portage/porthole
sudo DISTDIR=/var/cache/distfiles ebuild --force porthole-20260515-r1.ebuild manifest
```

If Portage still reports a BLAKE2B mismatch, remove the stale distfile and
repeat the distfile and Manifest steps:

```sh
sudo rm -f /var/cache/distfiles/porthole-20260515.tar.gz
```
You may need to add a line to package.accept_keywords:
```
# required by app-portage/porthole (argument)
=app-portage/porthole-20260515-r1 ~amd64
```
