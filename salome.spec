%define		srcv		src%{version}

# FIXME need (at least) distene/{api,blsurf}.h for BLSURFPLUGIN module
# HXX2SALOMEDOC are only documentation files
# TODO SAMPLES
# TODO NETGENPLUGIN (package functional built (but latest version 4.9.11, not salome's required 4.5) but needs extra work with salome integration)
%define		modules		 GHS3DPRLPLUGIN MULTIPR XDATA HELLO PYCALCULATOR YACS HexoticPLUGIN PYHELLO

Name:		salome
Group:		Sciences/Physics
Version:	5.1.3
Release:	%mkrel 1
Summary:	Pre- and Post-Processing for numerical simulation
License:	GPL
URL:		http://www.salome-platform.org
# http://www.salome-platform.org/downloads/salome-v5.1.3/DownloadDistr?platform=Sources&version=5.1.3
Source0:	src5.1.3.tar.gz
# http://www.salome-platform.org/downloads/salome-v5.1.3/DownloadDistr?platform=Documentation&version=5.1.3
Source1:	doc5.1.3.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

BuildRequires:	bison flex
BuildRequires:	boost-devel
BuildRequires:	cppunit-devel
BuildRequires:	doxygen
BuildRequires:	gcc-gfortran
BuildRequires:	GL-devel
BuildRequires:	graphviz
BuildRequires:	hdf5
BuildRequires:	hdf5-devel
BuildRequires:	libqwt-devel
BuildRequires:	libxml2-devel
BuildRequires:	omniorb-devel
BuildRequires:	opencascade-devel
BuildRequires:	openmpi-devel
BuildRequires:	python-omniidl
BuildRequires:	python-omniorb
BuildRequires:	python-qt4-devel
BuildRequires:	python-vtk-devel
BuildRequires:	qt4-devel
BuildRequires:	swig
BuildRequires:	vtk-devel
BuildRequires:	X11-devel
%py_requires -d

Patch0:		lib_location_suffix.patch
Patch1:		opencascade.patch
Patch2:		underlink.patch
Patch3:		format.patch
Patch4:		paramnames.patch
Patch5:		libc.patch
Patch6:		libxml2.patch
Patch7:		destdir.patch
Patch8:		undefined.patch

# Weird linking problem; this patch just prints the link failure message and
# calls abort if the code would ever follow the path with the undefined symbol...
Patch9:		FIXME.patch

%description
SALOME is an open-source software that provides a generic platform for
Pre- and Post-Processing for numerical simulation. It is based on an open
and flexible architecture made of reusable components.

SALOME is a cross-platform solution. It is distributed as open-source
software under the terms of the GNU LGPL license. You can download both
the source code and the executables from this site.

SALOME can be used as standalone application for generation of CAD models,
their preparation for numerical calculations and post-processing of the
calculation results.

SALOME can also be used as a platform for integration of the external
third-party numerical codes to produce a new application for the full
life-cycle management of CAD models.

#-----------------------------------------------------------------------
%prep
%setup -q -n %{srcv}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1

# want the kernel version that doesn't want to link to /usr/lib/lbxml.a
cp -f KERNEL_SRC_%{version}/salome_adm/unix/config_files/check_libxml.m4 MED_SRC_%{version}/adm_local/unix/config_files/check_libxml.m4

#-----------------------------------------------------------------------
# link with libraries in buildroot, not in _libdir
%define ldflags_buildroot	perl -pi -e 's|^(installed)=yes|$1=no|;' -e 's| (%{_libdir}/salome/lib\\w+\\.la)| %{buildroot}$1|g;' %{buildroot}%{_libdir}/salome/*la

%build
export KERNEL_ROOT_DIR=%{buildroot}%{_prefix}
export GUI_ROOT_DIR=%{buildroot}%{_prefix}
export MED_ROOT_DIR=%{buildroot}%{_prefix}
export GEOM_ROOT_DIR=%{buildroot}%{_prefix}
export SMESH_ROOT_DIR=%{buildroot}%{_prefix}
export RANDOMIZER_ROOT_DIR=%{buildroot}%{_prefix}
export VISU_ROOT_DIR=%{buildroot}%{_prefix}
export CASROOT=%{_datadir}/opencascade

pushd KERNEL_SRC_%{version}
    %configure								\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-openmpi=%{_prefix}					\
    %make
    %makeinstall_std
    %{ldflags_buildroot}
popd

pushd GUI_SRC_%{version}
    perl -pi								\
	-e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
	idl/.depidl
    sh ./build_configure
    %configure								\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-kernel=$KERNEL_ROOT_DIR					\
    %make
    %makeinstall_std
    %{ldflags_buildroot}
popd

for module in RANDOMIZER VISU LIGHT SIERPINSKY; do
    cp -f GUI_SRC_%{version}/adm_local/unix/config_files/check_GUI.m4 ${module}_SRC_%{version}/adm_local/unix/config_files
done

for module in MED GEOM; do
    pushd ${module}_SRC_%{version}
	if [ -f idl/.depidl ]; then
	    perl -pi							\
		-e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
		idl/.depidl
	fi
	sh ./build_configure
	%configure							\
	    --with-python-site=%{python_sitearch}			\
	    --with-python-site-exec=%{python_sitearch}			\
	    --with-openmpi=%{_prefix}					\
	    --with-kernel=$KERNEL_ROOT_DIR				\
	    --with-gui=$GUI_ROOT_DIR
	%make
	%makeinstall_std
	%{ldflags_buildroot}
    popd
done

pushd SMESH_SRC_%{version}
    perl -pi								\
	-e 's@ ((SALOME\w|GEOM_Gen)\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
	idl/.depidl
    sh ./build_configure
    %configure								\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-kernel=$KERNEL_ROOT_DIR					\
	--with-gui=$GUI_ROOT_DIR
    %make
    %makeinstall_std
    %{ldflags_buildroot}
popd

for module in PYLIGHT CALCULATOR HXX2SALOME COMPONENT RANDOMIZER VISU; do
    pushd ${module}_SRC_%{version}
	if [ -f idl/.depidl ]; then					\
	    perl -pi							\
		-e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
		idl/.depidl
	fi
	sh ./build_configure
	%configure							\
	    --with-python-site=%{python_sitearch}			\
	    --with-python-site-exec=%{python_sitearch}			\
	    --with-openmpi=%{_prefix}					\
	    --with-kernel=$KERNEL_ROOT_DIR				\
	    --with-gui=$GUI_ROOT_DIR
	%make
	%makeinstall_std
	%{ldflags_buildroot}
    popd
done

# fails if --with-gui option isn't either "yes" or "no", but properly
# "detects" it based on other shell variables
pushd LIGHT_SRC_%{version}
    perl -pi								\
    sh ./build_configure
    %configure								\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-kernel=$KERNEL_ROOT_DIR
    %make
    %makeinstall_std
    %{ldflags_buildroot}
popd

for module in %{modules}; do
    pushd ${module}_SRC_%{version}
	if [ -f idl/.depidl ]; then
	    perl -pi							\
		-e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
		idl/.depidl
	fi
	if [ -f ./build_configure ]; then
	    sh ./build_configure
	fi
	%configure							\
	    --with-python-site=%{python_sitearch}			\
	    --with-python-site-exec=%{python_sitearch}			\
	    --with-openmpi=%{_prefix}					\
	    --with-kernel=$KERNEL_ROOT_DIR				\
	    --with-gui=$GUI_ROOT_DIR
	%make
	%makeinstall_std
	%{ldflags_buildroot}
    popd
done

#-----------------------------------------------------------------------
%clean
rm -rf %{buildroot}

#-----------------------------------------------------------------------
%install
# link with libraries in _libdir, not in buildroot
perl -pi								\
    -e 's|^(installed)=no|$1=yes|;'					\
    -e 's| %{buildroot}(%{_libdir}/salome/lib\w\.la)| $1|g;'		\
    %{buildroot}%{_libdir}/salome/*la
