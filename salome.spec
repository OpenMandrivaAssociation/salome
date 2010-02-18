%define		srcv		src%{version}
%define		modules		MED GEOM SMESH BLSURFPLUGIN HXX2SALOMEDOC PYLIGHT CALCULATOR HXX2SALOME RANDOMIZER COMPONENT SAMPLES LIGHT SIERPINSKY GHS3DPLUGIN GHS3DPRLPLUGIN MULTIPR VISU NETGENPLUGIN XDATA HELLO PYCALCULATOR YACS HexoticPLUGIN PYHELLO


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
BuildRequires:	hdf5-devel
BuildRequires:	libqwt-devel
BuildRequires:	libxml2-devel
BuildRequires:	omniorb-devel
BuildRequires:	opencascade-devel
BuildRequires:	openmpi-devel
BuildRequires:	python-omniidl
BuildRequires:	python-omniorb
BuildRequires:	python-qt4-devel
BuildRequires:	qt4-devel
BuildRequires:	swig
BuildRequires:	vtk-devel
BuildRequires:	X11-devel
%py_requires -d

Patch0:		lib_location_suffix.patch
Patch1:		opencascade.patch
Patch2:		underlink.patch
Patch3:		format.patch

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

%prep
%setup -q -n %{srcv}

%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

# want the kernel version that doesn't want to link to /usr/lib/lbxml.a
cp -f KERNEL_SRC_%{version}/salome_adm/unix/config_files/check_libxml.m4 MED_SRC_%{version}/adm_local/unix/config_files/check_libxml.m4

%build
export KERNEL_ROOT_DIR=%{_builddir}/%{srcv}/KERNEL_SRC_%{version}
export MED_ROOT_DIR=%{_builddir}/%{srcv}/MED_SRC_%{version}
export GEOM_ROOT_DIR=%{_builddir}/%{srcv}/GEOM_SRC_%{version}
export SMESH_ROOT_DIR=%{_builddir}/%{srcv}/SMESH_SRC_%{version}
export CASROOT=%{_datadir}/opencascade

pushd KERNEL_SRC_%{version}
    %configure						\
	--with-python-site=%{python_sitearch}		\
	--with-python-site-exec=%{python_sitearch}	\
	--with-openmpi=%{_prefix}			\
    %make
    %makeinstall_std
popd

# most of remaining build wants it in the directory layout after make install
export KERNEL_ROOT_DIR=%{buildroot}%{_prefix}

pushd GUI_SRC_%{version}
    perl -pi						\
	-e 's@ (SALOME(DS|_Component)\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;'	\
	idl/.depidl
    sh ./build_configure
    %configure						\
	--with-python-site=%{python_sitearch}		\
	--with-python-site-exec=%{python_sitearch}	\
	--with-kernel=$KERNEL_ROOT_DIR			\
    %make
    %makeinstall_std
popd

for module in %{modules}; do
    pushd ${module}_SRC_%{version}
	sh ./build_configure
	%configure					\
	    --with-python-site=%{python_sitearch}	\
	    --with-python-site-exec=%{python_sitearch}	\
	    --with-openmpi=%{_prefix}			\
	    --with-kernel=$KERNEL_ROOT_DIR		\
	    --with-gui=%{buildroot}
	%make
    popd
done

#-----------------------------------------------------------------------
%clean
rm -rf %{buildroot}

#-----------------------------------------------------------------------
%install
for module in %{modules}; do
    pushd $module_SRC_%{version}
	%makeinstall_std
    popd
done
