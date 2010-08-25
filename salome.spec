%define		srcv		src%{version}

# BLSURFPLUGIN cannot be built because it requires "a BLSURF sdk"
#	see BUILD/src5.1.3/BLSURFPLUGIN_SRC_5.1.3/README for details
%define		modules		GHS3DPRLPLUGIN HELLO PYCALCULATOR YACS MULTIPR HexoticPLUGIN PYHELLO NETGENPLUGIN

Name:		salome
Group:		Sciences/Physics
Version:	5.1.4
Release:	%mkrel 1
Summary:	Pre- and Post-Processing for numerical simulation
License:	GPL
URL:		http://www.salome-platform.org
Source0:	http://files.opencascade.com/Salome/Salome%{version}/src%{version}.tar.gz

# Not really required, but not all documentation is regenerated, so,
# for easier acess, keep it in the srpm
# http://www.salome-platform.org/downloads/salome-v5.1.3/DownloadDistr?platform=Documentation&version=5.1.3
Source1:	http://files.opencascade.com/Salome/Salome%{version}/doc%{version}.tar.gz

Source2:	salome.png
Source3:	salome32.png

# http://www.salome-platform.org/forum/forum_9/thread_1416
Source4:	netgen-4.5_SRC.tar.gz

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
BuildRequires:	med-devel
BuildRequires:	metis
BuildRequires:	metis-devel
BuildRequires:	omniorb
BuildRequires:	omniorb-devel
BuildRequires:	omninotify-devel
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
BuildRequires:	scotch
BuildRequires:	scotch-devel
BuildRequires:	swig
BuildRequires:	tetex-dvips
BuildRequires:	tetex-latex
BuildRequires:	togl
BuildRequires:	vtk-devel
BuildRequires:	X11-devel
%py_requires -d

Requires:	libopencascade
Requires:	libopencascade-devel
Requires:	omninotify
Requires:	omniorb
Requires:	opencascade
Requires:	python-omniorb

Patch0:		lib_location_suffix.patch
Patch1:		opencascade.patch
Patch2:		underlink.patch
Patch3:		format.patch
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

Patch14:	scotch.patch
Patch15:	metis.patch

Patch16:	netgen4.5ForSalome.patch

# https://bugzilla.gnome.org/show_bug.cgi?id=616344
Patch17:	workaround-doxygen-1.6.3-bug.patch

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

%package	samples
Group:		Sciences/Physics
Summary:	Sample files for salome-platform

%description	samples
This package contains salome-platform samples.

#-----------------------------------------------------------------------
%prep
%setup -q -n %{srcv}
%setup -q -n %{srcv} -T -D -a 4

%patch0 -p1 -b .lib_suff
%patch1 -p1
%patch2 -p1 -b .link
%patch3 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1 -b .include
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1

if [ `rpm -q --qf "%%{version}" doxygen` = "1.6.3" ]; then
#%patch17 -p1
fi

# want the kernel version that doesn't want to link to /usr/lib/lbxml.a
cp -f KERNEL_SRC_%{version}/salome_adm/unix/config_files/check_libxml.m4 MED_SRC_%{version}/adm_local/unix/config_files/check_libxml.m4

#-----------------------------------------------------------------------
# link with libraries in buildroot, not in _libdir
%define ldflags_buildroot	perl -pi -e 's|^(installed)=yes|$1=no|;' -e 's| (%{_libdir}/salome/lib\\w+\\.la)| %{buildroot}$1|g;' %{buildroot}%{_libdir}/salome/*la

%build

%ifarch X86_64 ppc64
    export CXXFLAGS="$CXXFLAGS -fPIC"
%endif

export CASROOT=%{_datadir}/opencascade

# lots of hacks here, to resolve symbols and such...
pushd netgen-4.5_SRC
    sh makeForSalome.sh
    pushd ngtcltk
	g++ $CXXFLAGS -DOPENGL=1 -DOCCGEOMETRY=1 -DSOCKETS=1 -DHAVE_CONFIG_H=1 -o ngpkg.o -c ngpkg.cpp -I ../libsrc/include -I${CASROOT}/inc
%ifarch X86_64 ppc64
	cp -f ngpkg.o ../install/lib/LINUX64
%else
	cp -f ngpkg.o ../install/lib/LINUX
%endif
    popd
popd

export KERNEL_ROOT_DIR=%{buildroot}%{_prefix}
export GUI_ROOT_DIR=%{buildroot}%{_prefix}
export MED_ROOT_DIR=%{buildroot}%{_prefix}
export GEOM_ROOT_DIR=%{buildroot}%{_prefix}
export SMESH_ROOT_DIR=%{buildroot}%{_prefix}
export RANDOMIZER_ROOT_DIR=%{buildroot}%{_prefix}
export VISU_ROOT_DIR=%{buildroot}%{_prefix}

pushd KERNEL_SRC_%{version}
    sh ./build_configure
    %configure2_5x							\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-openmpi=%{_prefix}
    make
    %makeinstall_std
    %{ldflags_buildroot}
popd

pushd GUI_SRC_%{version}
    sh ./build_configure
    perl -pi								\
	-e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
	idl/.depidl
    %configure2_5x							\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-kernel=$KERNEL_ROOT_DIR
    make
    %makeinstall_std
    %{ldflags_buildroot}
popd

for module in RANDOMIZER VISU LIGHT SIERPINSKY PYHELLO NETGENPLUGIN; do
    cp -f GUI_SRC_%{version}/adm_local/unix/config_files/check_GUI.m4 ${module}_SRC_%{version}/adm_local/unix/config_files
done

for module in MED GEOM; do
    pushd ${module}_SRC_%{version}
	sh ./build_configure
	perl -pi							\
	    -e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
	    idl/.depidl
	%configure2_5x							\
	    --with-python-site=%{python_sitearch}			\
	    --with-python-site-exec=%{python_sitearch}			\
	    --with-openmpi=%{_prefix}					\
	    --with-med2=%{_prefix}					\
	    --with-scotch=%{_prefix}					\
	    --with-kernel=$KERNEL_ROOT_DIR				\
	    --with-gui=$GUI_ROOT_DIR
	make
	%makeinstall_std
	%{ldflags_buildroot}
    popd
done

pushd SMESH_SRC_%{version}
    sh ./build_configure
    perl -pi								\
	-e 's@ ((SALOME\w|GEOM_Gen)\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
	idl/.depidl
    %configure2_5x							\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-kernel=$KERNEL_ROOT_DIR					\
	--with-gui=$GUI_ROOT_DIR
    make
    %makeinstall_std
    %{ldflags_buildroot}
popd

for module in PYLIGHT CALCULATOR HXX2SALOME COMPONENT RANDOMIZER VISU; do
    pushd ${module}_SRC_%{version}
	sh ./build_configure
	if [ -f idl/.depidl ]; then					\
	    perl -pi							\
		-e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
		idl/.depidl
	fi
	%configure2_5x							\
	    --with-python-site=%{python_sitearch}			\
	    --with-python-site-exec=%{python_sitearch}			\
	    --with-openmpi=%{_prefix}					\
	    --with-med2=%{_prefix}					\
	    --with-scotch=%{_prefix}					\
	    --with-kernel=$KERNEL_ROOT_DIR				\
	    --with-gui=$GUI_ROOT_DIR
	make
	%makeinstall_std
	%{ldflags_buildroot}
    popd
done

# fails if --with-gui option isn't either "yes" or "no", but properly
# "detects" it based on other shell variables
pushd LIGHT_SRC_%{version}
    sh ./build_configure
    %configure2_5x							\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-kernel=$KERNEL_ROOT_DIR
    make
    %makeinstall_std
    %{ldflags_buildroot}
popd

# FIXME Avoid build failure - not paralell make safe
mkdir -p %{buildroot}%{_datadir}/xdata/templates
mkdir -p XDATA_SRC_%{version}/lib/python%{py_ver}/site-packages/xdata
pushd XDATA_SRC_%{version}
    %configure2_5x
    make
    %makeinstall_std
    %{ldflags_buildroot}
popd

for module in %{modules}; do
    pushd ${module}_SRC_%{version}
	if [ -f ./build_configure ]; then
	    sh ./build_configure
	fi
	if [ -f idl/.depidl ]; then
	    perl -pi							\
		-e 's@ (SALOME\w+\.idl)@ %{buildroot}%{_prefix}/idl/salome/$1@g;' \
		idl/.depidl
	fi
	%configure2_5x							\
	    --with-python-site=%{python_sitearch}			\
	    --with-python-site-exec=%{python_sitearch}			\
	    --with-qsci4-includes=%{qt4include}				\
	    --with-qsci4-libraries=%{_libdir}				\
	    --with-openmpi=%{_prefix}					\
	    --with-med2=%{_prefix}					\
	    --with-scotch=%{_prefix}					\
	    --with-kernel=$KERNEL_ROOT_DIR				\
	    --with-gui=$GUI_ROOT_DIR					\
	    --with-netgen=%{_builddir}/src5.1.3/netgen-4.5_SRC/install
	make
	%makeinstall_std
	%{ldflags_buildroot}
    popd
done

#-----------------------------------------------------------------------
%clean
#rm -rf %{buildroot}

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

# FIXME need to patch some code because just setting PYTHONPATH is not
# enough to get it to find some python packages (from C++ code linked
# to libpython)
#-----------------------------------------------------------------------
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
export CASROOT=%{_datadir}/opencascade
export CSF_GraphicShr=%{_libdir}/libTKOpenGl.so.0.0.0
export LD_LIBRARY_PATH=%{_libdir}/salome:\$LD_LIBRARY_PATH

# Extra debug information
export MESA_DEBUG=FP
export LIBGL_DEBUG=verbose

# Force software rendering
export LIBGL_ALWAYS_INDIRECT=true

cd %{py_platsitedir}/salome
%{_bindir}/%{name}/runSalome "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/runSalome
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
cat > %{buildroot}%{_bindir}/killSalome << EOF
#!/bin/sh

PIDS=\`ps x |
egrep '\<(notifd|SALOME_Session_Server|SALOME_LauncherServer|SALOME_ConnectionManagerServer|FactoryServerPy|omniNames)\>' |
grep -v egrep |
awk '{ print \$1; }'\`
[ -z "\$PIDS" ] || kill \$PIDS
EOF
chmod +x %{buildroot}%{_bindir}/killSalome
#-----------------------------------------------------------------------

# some files in %py_puresitedir uses interfaces to load dynamic modules
# but want the files in the same directory, not %py_platsitedir
%ifarch x86_64 ppc64
  pushd %{buildroot}%{py_puresitedir}
    mv -f %{name}/* %{buildroot}%{py_platsitedir}/%{name}
    mv -f xdata %{buildroot}%{py_platsitedir}
    rmdir %{name}
  popd
%endif

rm -f %{buildroot}%{py_platsitedir}/%{name}/*.a
mv -f %{buildroot}%{_libdir}/%{name}/_libSALOME_Swig.* %{buildroot}%{py_platsitedir}/%{name}
mv -f %{buildroot}%{_bindir}/%{name}/libSALOME_Swig.py %{buildroot}%{py_platsitedir}/%{name}

mkdir -p %{buildroot}%{_datadir}/%{name}/samples
cp -far SAMPLES_SRC_%{version}/* %{buildroot}%{_datadir}/%{name}/samples
cp -fa HXX2SALOMEDOC_SRC_%{version}/*  %{buildroot}%{_docdir}/%{name}

install -m644 -D %{SOURCE2} %{buildroot}%{_miconsdir}/%{name}.png
install -m644 -D %{SOURCE3} %{buildroot}%{_iconsdir}/%{name}.png
install -m644 -D %{SOURCE3} %{buildroot}%{_datadir}/pixmaps/%{name}.png
mkdir -p %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Salome
Comment=Pre- and Post-Processing for numerical simulation
Exec=runSalome
Icon=%{name}
Terminal=false
Type=Application
Categories=Science;Physics;
EOF

#-----------------------------------------------------------------------
%files
%defattr(-,root,root)
%{_bindir}/runSalome
%{_bindir}/killSalome
%dir %{_datadir}/idl/salome
%{_datadir}/idl/salome/*
%dir %{py_platsitedir}/%{name}
%{py_platsitedir}/%{name}/*
%dir %{py_platsitedir}/xdata
%{py_platsitedir}/xdata/*
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/resources
%{_datadir}/%{name}/resources/*
%dir %{_datadir}/%{name}/salome_adm
%{_datadir}/%{name}/salome_adm/*
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
%{_miconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_datadir}/pixmaps/%{name}.png
%{_datadir}/applications/mandriva-%{name}.desktop

#-----------------------------------------------------------------------
%files		samples
%defattr(-,root,root)
%dir %{_datadir}/%{name}/HXX2SALOME_Test
%{_datadir}/%{name}/HXX2SALOME_Test/*
%dir %{_datadir}/%{name}/samples
%{_datadir}/%{name}/samples/*
%dir %{_datadir}/%{name}/Tests
%{_datadir}/%{name}/Tests/*
%dir %{_datadir}/%{name}/yacssamples
%{_datadir}/%{name}/yacssamples/*
%dir %{_datadir}/%{name}/yacssupervsamples
%{_datadir}/%{name}/yacssupervsamples/*
