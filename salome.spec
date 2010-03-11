%define		srcv		src%{version}

# FIXME need (at least) distene/{api,blsurf}.h for BLSURFPLUGIN module
# HXX2SALOMEDOC are only documentation files
# TODO SAMPLES
# TODO NETGENPLUGIN (package functional built (but latest version 4.9.11, not salome's required 4.5) but needs extra work with salome integration)
# TODO MULTIPR needs metis
%define		modules		GHS3DPRLPLUGIN XDATA HELLO PYCALCULATOR YACS HexoticPLUGIN PYHELLO

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
BuildRequires:	graphviz-devel
BuildRequires:	hdf5
BuildRequires:	hdf5-devel
BuildRequires:	libopencascade-devel
BuildRequires:	libqwt-devel
BuildRequires:	libxml2-devel
BuildRequires:	omniorb
BuildRequires:	omniorb-devel
BuildRequires:	omninotify-devel

# FIXME not really required, but matches the autoconf macro requirements
# based on directory layout bellow $CASROOT
BuildRequires:	opencascade

BuildRequires:	openmpi
BuildRequires:	openmpi-devel
BuildRequires:	python-omniidl
BuildRequires:	python-omniorb
BuildRequires:	python-qt4-devel
BuildRequires:	python-sphinx
BuildRequires:	python-vtk-devel
BuildRequires:	qt4-devel
BuildRequires:	qscintilla-qt4-devel
BuildRequires:	swig
BuildRequires:	tetex-dvips
BuildRequires:	tetex-latex
BuildRequires:	vtk-devel
BuildRequires:	X11-devel
%py_requires -d

Requires:	omninotify

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

#  There is also a include order change in underlink.patch
#  The reason is YACS code using Node.hxx from INTERP_KERNEL, and not
# YACS/src/engine due to adding -I$(KERNEL_ROOT_DIR)/include/salome before
# "local" includes
Patch10:	includeorder.patch

Patch11:	prefix.patch
Patch12:	runtime.patch

# Build still stops in install of XDATA_SRC_5.1.3/src/XDATA2SALOME/tests
# just don't build or install anything from there for now
Patch13:	xdata-destdir.patch

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
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1

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
    sh ./build_configure
    %configure								\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-openmpi=%{_prefix}
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
	--with-kernel=$KERNEL_ROOT_DIR
    %make
    %makeinstall_std
    %{ldflags_buildroot}
popd

for module in RANDOMIZER VISU LIGHT SIERPINSKY PYHELLO; do
    cp -f GUI_SRC_%{version}/adm_local/unix/config_files/check_GUI.m4 ${module}_SRC_%{version}/adm_local/unix/config_files
done

# MED is not parallel make safe
# FIXME *possibly* adding libmedmemloader.la to LIBADD would correct the issue:
##	mv -f .deps/_libParaMEDMEM_Swig_la-libParaMEDMEM_Swig_wrap.Tpo .deps/_libParaMEDMEM_Swig_la-libParaMEDMEM_Swig_wrap.Plo
##	/bin/sh ../../libtool --tag=CXX   --mode=link x86_64-mandriva-linux-gnu-g++ -I/home/mandrake/rpm/BUILDROOT/salome-5.1.3-1mdv2010.1.x86_64/usr/include/salome -include SALOMEconfig.h -D_OCC64 -O2 -g -pipe -Wformat -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -fstack-protector --param=ssp-buffer-size=4 -g -D_DEBUG_  -g -Wparentheses -Wreturn-type -Wmissing-declarations -Wunused -pthread -module  -lhdf5  -L/usr/lib64/python2.6/config -lpython2.6 -ldl -lutil -pthread -L/usr/lib64 -lmpi_cxx -lmpi -lopen-rte -lopen-pal -libverbs -ltorque -lnuma -ldl -Wl,--export-dynamic -lnsl -lutil -lm -ldl ../MEDCoupling/libmedcoupling.la ../INTERP_KERNEL/libinterpkernel.la ../ParaMEDMEM/libparamedmem.la ../ParaMEDMEM/MEDLoader/libparamedmemmedloader.la -L/home/mandrake/rpm/BUILDROOT/salome-5.1.3-1mdv2010.1.x86_64/usr/lib64/salome -lSALOMELocalTrace -Wl,--as-needed -Wl,--no-undefined -Wl,-z,relro -Wl,-O1 -Wl,--as-needed -Wl,--no-undefined -Wl,-z,relro -Wl,-O1 -Wl,--as-needed -Wl,--no-undefined -Wl,-z,relro -Wl,-O1 -Xlinker -enable-new-dtags -o _libParaMEDMEM_Swig.la -rpath /usr/lib64/salome  _libParaMEDMEM_Swig_la-libParaMEDMEM_Swig_wrap.lo  -lnsl -lm -lrt -ldl  
##	libtool: link: cannot find the library `../ParaMEDMEM/MEDLoader/libparamedmemmedloader.la' or unhandled argument `../ParaMEDMEM/MEDLoader/libparamedmemmedloader.la'
##	make[2]: *** [_libParaMEDMEM_Swig.la] Error 1
##	make[2]: Leaving directory `/home/mandrake/rpm/BUILD/src5.1.3/MED_SRC_5.1.3/src/ParaMEDMEM_Swig'
##	make[1]: *** [all-recursive] Error 1
 pushd MED_SRC_%{version}
    perl -pi								\
	-e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
	idl/.depidl
    sh ./build_configure
    %configure								\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-openmpi=%{_prefix}					\
	--with-kernel=$KERNEL_ROOT_DIR					\
	--with-gui=$GUI_ROOT_DIR
    make
    %makeinstall_std
    %{ldflags_buildroot}
popd

pushd GEOM_SRC_%{version}
    perl -pi								\
	-e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
	idl/.depidl
    sh ./build_configure
    %configure								\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-openmpi=%{_prefix}					\
	--with-kernel=$KERNEL_ROOT_DIR					\
	--with-gui=$GUI_ROOT_DIR
    %make
    %makeinstall_std
    %{ldflags_buildroot}
popd

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
    sh ./build_configure
    %configure								\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-kernel=$KERNEL_ROOT_DIR
    %make
    %makeinstall_std
    %{ldflags_buildroot}
popd

# FIXME Avoid build failure
# FIXME make install should create the directory
mkdir -p %{buildroot}%{_datadir}/xdata/templates

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
	    --with-qsci4-includes=%{qt4include}				\
	    --with-qsci4-libraries=%{_libdir}				\
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

mkdir -p %{buildroot}%{_datadir}/idl
if [ -d %{buildroot}%{_prefix}/idl ]; then
    mv -f %{buildroot}%{_prefix}/idl %{buildroot}%{_datadir}
fi
mkdir -p %{buildroot}%{_datadir}/%{name}
mv -f %{buildroot}%{_bindir}/HXX2SALOME_Test %{buildroot}%{_datadir}/%{name}
mv -f %{buildroot}%{_prefix}/Tests %{buildroot}%{_datadir}/%{name}
mv -f %{buildroot}%{_prefix}/salome_adm %{buildroot}%{_datadir}/%{name}
mv -f %{buildroot}%{_prefix}/adm_local/cmake_files/* %{buildroot}%{_datadir}/%{name}/salome_adm/cmake_files
mv -f %{buildroot}%{_prefix}/adm_local/unix/config_files/* %{buildroot}%{_datadir}/%{name}/salome_adm/unix/config_files

# apparently instaled by mistake (nodist, and in purebindir)
rm -f %{buildroot}%{_bindir}/runTestMedCorba

# something wrong in make install
rm -f %{buildroot}%{py_puresitedir}/xdata/.dummy.py*

cat > %{buildroot}%{_bindir}/runSalome << EOF
#!/bin/sh

export KERNEL_ROOT_DIR=%{_prefix}
export PYCALCULATOR_ROOT_DIR=%{_prefix}
export PYHELLO_ROOT_DIR=%{_prefix}
export LIGHT_ROOT_DIR=%{_prefix}
export COMPONENT_ROOT_DIR=%{_prefix}
export MED_ROOT_DIR=%{_prefix}
export VISU_ROOT_DIR=%{_prefix}
export SMESH_ROOT_DIR=%{_prefix}
export GEOM_ROOT_DIR=%{_prefix}
export GUI_ROOT_DIR=%{_prefix}
export YACS_ROOT_DIR=%{_prefix}
export LD_LIBRARY_PATH=%{_libdir}/salome:\$LD_LIBRARY_PATH
cd %{py_puresitedir}
%{_bindir}/%{name}/runSalome "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/runSalome

# some files in %py_puresitedir uses interfaces to load dynamic modules
# but want the files in the same directory, not %py_platsitedir
%ifarch x86_64 ppc64
  pushd %{buildroot}%{py_puresitedir}
    mv -f %{name}/* %{buildroot}%{py_platsitedir}/%{name}
    mv -f xdata %{buildroot}%{py_platsitedir}
    rmdir %{name}
  popd
%endif

rm -f %{buildroot}%{py_puresitedir}/%{name}/*.a
mv -f %{buildroot}%{_libdir}/%{name}/_libSALOME_Swig.* %{buildroot}%{py_puresitedir}/%{name}
mv -f %{buildroot}%{_bindir}/%{name}/libSALOME_Swig.py %{buildroot}%{py_puresitedir}/%{name}

#-----------------------------------------------------------------------
%files
%defattr(-,root,root)
%{_bindir}/runSalome
%dir %{_datadir}/idl/salome
%{_datadir}/idl/salome/*
%dir %{py_platsitedir}/%{name}
%{py_platsitedir}/%{name}/*
%dir %{py_platsitedir}/xdata
%{py_platsitedir}/xdata/*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/*
%dir %{_datadir}/xdata
%{_datadir}/xdata/*
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%dir %{_docdir}/%{name}
%{_docdir}/%{name}/*
%dir %{_bindir}/%{name}
%{_bindir}/%{name}/*
%dir %{_docdir}/xdata-0.7.3
%{_docdir}/xdata-0.7.3/*
