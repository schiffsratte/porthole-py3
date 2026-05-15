# Copyright 2026 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=8

DISTUTILS_USE_PEP517=setuptools
PYTHON_COMPAT=( python3_12 )

inherit distutils-r1 xdg

DESCRIPTION="GTK frontend for Gentoo package management"
HOMEPAGE="https://github.com/schiffsratte/porthole-py3"
SRC_URI="${P}.tar.gz"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~amd64 ~x86"
RESTRICT="mirror"

RDEPEND="
	dev-python/pkgcore[${PYTHON_USEDEP}]
	dev-python/pygobject:3[${PYTHON_USEDEP}]
	sys-apps/portage[${PYTHON_USEDEP}]
	x11-libs/gtk+:3[introspection]
	x11-libs/gtksourceview:4[introspection]
"
DEPEND="${RDEPEND}"

src_prepare() {
	default
	distutils-r1_src_prepare
}
