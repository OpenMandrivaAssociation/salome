%define		srcv			src%{version}

# BLSURFPLUGIN cannot be built because it requires "a BLSURF sdk"
#	see BUILD/src6.3.1/BLSURFPLUGIN_SRC_6.3.1/README for details
%define		modules			GHS3DPRLPLUGIN HELLO PYCALCULATOR YACS HexoticPLUGIN PYHELLO NETGENPLUGIN
%define		extra_modules		GHS3DPLUGIN HEXABLOCK HEXABLOCKPLUGIN HOMARD JOBMANAGER

%define		build_root		%{_builddir}/%{srcv}/build_root
%define		salome_makeinstall_std	make DESTDIR=%{build_root} install

Name:		salome
Group:		Sciences/Physics
Version:	6.3.1
Release:	%mkrel 1
Summary:	Pre- and Post-Processing for numerical simulation
License:	GPL
URL:		http://www.salome-platform.org
# http://www.salome-platform.org/downloads/salome-v6.3.1/DownloadDistr?platform=Sources&version=6.3.1
Source0:	src%{version}.tar.gz

# http://www.salome-platform.org/forum/forum_9/thread_1416
Source1:	netgen-4.5_SRC.tar.gz

# Not really required, kept in case changing to no longer regenerate
# documentation, as done in some packages to save build system time,
# also, the normal build may not rebuild all documentation, or may
# have some issues like the doxygen double underscore issue
# http://www.salome-platform.org/downloads/salome-v6.3.1/DownloadDistr?platform=Documentation&version=6.3.1
Source2:	doc%{version}.tar.gz

Source3:	salome.png
Source4:	salome32.png

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
BuildRequires:	opencascade-devel
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
BuildRequires:	texlive
BuildRequires:	togl
BuildRequires:	vtk-devel
BuildRequires:	libx11-devel
BuildRequires:	python-devel

Requires:	libopencascade
Requires:	libopencascade-devel
Requires:	omninotify
Requires:	omniorb
Requires:	opencascade
Requires:	openmpi
Requires:	python-omniorb

Patch0:		lib_location_suffix.patch
Patch1:		opencascade.patch
Patch2:		underlink.patch
Patch3:		format.patch
Patch4:		destdir.patch
Patch5:		undefined.patch

# Weird linking problem; this patch just prints the link failure message and
# calls abort if the code would ever follow the path with the undefined symbol...
Patch6:		FIXME.patch

#  There is also a include order change in underlink.patch
#  The reason is YACS code using Node.hxx from INTERP_KERNEL, and not
# YACS/src/engine due to adding -I$(KERNEL_ROOT_DIR)/include/salome before
# "local" includes
Patch7:		includeorder.patch

Patch8:		prefix.patch
Patch9:		runtime.patch
Patch10:	metis.patch
Patch11:	netgen4.5ForSalome.patch
Patch12:	help-prefix-path.patch
Patch13:	python-console-in-qt4.4+.patch

# Hack, not supported by newer qt4
# http://www.salome-platform.org/forum/forum_9/508970876
Patch14:	qobject_static_cast.patch

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
rm -fr %{srcv}
%setup -q -c -n %{srcv} -D -a 1

%patch0 -p1 -b .lib_suff
%patch1 -p1
%patch2 -p1 -b .link
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1 -b .include
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1

# want the kernel version that doesn't want to link to /usr/lib/lbxml.a
cp -f KERNEL_SRC_%{version}/salome_adm/unix/config_files/check_libxml.m4 MED_SRC_%{version}/adm_local/unix/config_files/check_libxml.m4

#-----------------------------------------------------------------------
%build
# link with libraries in build_root, not in _libdir
%define ldflags_build_root	perl -pi -e 's|^(installed)=yes|$1=no|;' -e 's| (%{_libdir}/salome/lib\\w+\\.la)| %{build_root}$1|g;' %{build_root}%{_libdir}/salome/*la

mkdir -p %{build_root}

export CASROOT=%{_datadir}/opencascade

pushd netgen-4.5_SRC
  %ifarch x86_64 ppc64
    export CXXFLAGS="$CXXFLAGS -DPIC -fPIC"
  %endif
    sh makeForSalome.sh
    pushd ngtcltk
        g++ $CXXFLAGS -DOPENGL=1 -DOCCGEOMETRY=1 -DSOCKETS=1 -DHAVE_CONFIG_H=1 -o ngpkg.o -c ngpkg.cpp -I ../libsrc/include -I${CASROOT}/inc
  %ifarch x86_64 ppc64
	cp -f ngpkg.o ../install/lib/LINUX64
  %else
	cp -f ngpkg.o ../install/lib/LINUX
  %endif
     popd
popd

export KERNEL_ROOT_DIR=%{build_root}%{_prefix}
export GUI_ROOT_DIR=%{build_root}%{_prefix}
export MED_ROOT_DIR=%{build_root}%{_prefix}
export GEOM_ROOT_DIR=%{build_root}%{_prefix}
export SMESH_ROOT_DIR=%{build_root}%{_prefix}
export RANDOMIZER_ROOT_DIR=%{build_root}%{_prefix}
export VISU_ROOT_DIR=%{build_root}%{_prefix}
export ATOMGEN_ROOT_DIR=%{build_root}%{_prefix}
export HEXABLOCK_ROOT_DIR=%{build_root}%{_prefix}
export PYTHONPATH=%{build_root}%{py_sitedir}/salome:%{build_root}%{py_platsitedir}/salome:%{build_root}%{_bindir}/salome
export LD_LIBRARY_PATH=%{build_root}%{_libdir}/salome:%{build_root}%{py_platsitedir}/salome

pushd KERNEL_SRC_%{version}
    sh ./build_configure
    %configure2_5x							\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-openmpi=%{_prefix}
    make
    %salome_makeinstall_std
    %{ldflags_build_root}
popd

pushd GUI_SRC_%{version}
    sh ./build_configure
    perl -pi								\
	-e 's@ (SALOME\w+\.idl)@ %{build_root}%{_prefix}/idl/salome/$1@g;' \
	idl/.depidl
    %configure2_5x							\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-kernel=$KERNEL_ROOT_DIR
    make
    %salome_makeinstall_std
    %{ldflags_build_root}
popd

for module in RANDOMIZER VISU LIGHT SIERPINSKY PYHELLO NETGENPLUGIN; do
    cp -f GUI_SRC_%{version}/adm_local/unix/config_files/check_GUI.m4 ${module}_SRC_%{version}/adm_local/unix/config_files
done

for module in MED GEOM; do
    pushd ${module}_SRC_%{version}
	sh ./build_configure
	perl -pi							\
	    -e 's@ (SALOME\w+\.idl)@ %{build_root}%{_prefix}/idl/salome/$1@g;' \
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
        %salome_makeinstall_std
        %{ldflags_build_root}
    popd
done

pushd SMESH_SRC_%{version}
    sh ./build_configure
    perl -pi								\
	-e 's@ ((SALOME\w|GEOM_Gen)\.idl)@ %{build_root}%{_prefix}/idl/salome/$1@g;' \
	idl/.depidl
    %configure2_5x							\
	--with-python-site=%{python_sitearch}				\
	--with-python-site-exec=%{python_sitearch}			\
	--with-med2=%{_prefix}						\
	--with-kernel=$KERNEL_ROOT_DIR					\
	--with-gui=$GUI_ROOT_DIR
    make
    %salome_makeinstall_std
    %{ldflags_build_root}
popd

for module in PYLIGHT CALCULATOR HXX2SALOME COMPONENT RANDOMIZER VISU; do
    pushd ${module}_SRC_%{version}
	sh ./build_configure
	if [ -f idl/.depidl ]; then					\
	    perl -pi							\
		-e 's@ (SALOME\w+\.idl)@ %{build_root}%{_prefix}/idl/salome/$1@g;' \
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
        %salome_makeinstall_std
        %{ldflags_build_root}
    popd
done

# fails if --with-gui option isn't either "yes" or "no", but properly
# "detects" it based on other shell variables
for module in LIGHT ATOMGEN ATOMIC ATOMSOLV; do
    pushd ${module}_SRC_%{version}
	sh ./build_configure
	%configure2_5x							\
	    --with-python-site=%{python_sitearch}			\
	    --with-python-site-exec=%{python_sitearch}			\
	    --with-kernel=$KERNEL_ROOT_DIR
	make
	%salome_makeinstall_std
	%{ldflags_build_root}
    popd
done

# FIXME broken cmake config files in paraview-devel
# and the one included has %#{buildroot} on it
%if 0
pushd PARAVIS_SRC_%{version}
    %cmake
    %make
    %salome_makeinstall_std
    %{ldflags_build_root}
popd
%endif

export KERNEL_CXXFLAGS=$KERNEL_ROOT_DIR/include/salome
for module in %{modules} %{extra_modules}; do
    pushd ${module}_SRC_%{version}
	if [ -f ./build_configure ]; then
	    sh ./build_configure
	fi
	if [ -f idl/.depidl ]; then
	    perl -pi							\
		-e 's@ (SALOME\w+\.idl)@ %{build_root}%{_prefix}/idl/salome/$1@g;' \
		-e 's@ (SMESH\w+\.idl)@ %{build_root}%{_prefix}/idl/salome/$1@g;'  \
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
	    --with-netgen=%{_builddir}/src%{version}/netgen-4.5_SRC/install
	make
        %salome_makeinstall_std
        %{ldflags_build_root}
    popd
done

# FIXME install as is TUTORIAL and in samples subpackage?

#-----------------------------------------------------------------------
%install

# link with libraries in _libdir, not in build_root	 
perl -pi								\
    -e 's|^(installed)=no|$1=yes|;'					\
    -e 's|%{build_root}||g;'						\
    %{build_root}%{_libdir}/salome/*.la	 

mkdir -p %{build_root}%{_datadir}/idl
if [ -d %{build_root}%{_prefix}/idl ]; then
    mv -f %{build_root}%{_prefix}/idl/* %{build_root}%{_datadir}/idl
fi
mkdir -p %{build_root}%{_datadir}/%{name}
mv -f %{build_root}%{_bindir}/HXX2SALOME_Test %{build_root}%{_datadir}/%{name}
mv -f %{build_root}%{_prefix}/Tests %{build_root}%{_datadir}/%{name}
mv -f %{build_root}%{_prefix}/salome_adm %{build_root}%{_datadir}/%{name}
mv -f %{build_root}%{_prefix}/adm_local/cmake_files/* %{build_root}%{_datadir}/%{name}/salome_adm/cmake_files
mv -f %{build_root}%{_prefix}/adm_local/unix/config_files/* %{build_root}%{_datadir}/%{name}/salome_adm/unix/config_files

# apparently instaled by mistake (nodist, and in purebindir)
rm -f %{build_root}%{_bindir}/runTestMedCorba

# doxygen 1.7.3 does not replicate good enough what was generated
# by doxygen 1.4*, so use the prebuilt files
pushd %{build_root}%{_docdir}
    rm -fr salome/*
    tar zxf %{SOURCE2}
    for top in KERNEL GEOM GUI HELLO MED PYHELLO SMESH VISU YACS; do
	for sub in doc%{version}/$top/*; do
	    cp -far $sub salome
	done
    done
    rm -fr doc%{version}
    find salome -type f | xargs chmod 0644
    find salome -type d | xargs chmod 0755
popd

# FIXME need to patch some code because just setting PYTHONPATH is not
# enough to get it to find some python packages (from C++ code linked
# to libpython)
#-----------------------------------------------------------------------
cat > %{build_root}%{_bindir}/runSalome << EOF
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
export PYTHONPATH=%{py_platsitedir}/salome:%{_bindir}/salome:%{_libdir}/salome

# Extra debug information
export MESA_DEBUG=FP
export LIBGL_DEBUG=verbose

# Force indirect rendering
export LIBGL_ALWAYS_INDIRECT=true

cd %{py_platsitedir}/salome
%{_bindir}/%{name}/runSalome "\$@"
EOF
chmod +x %{build_root}%{_bindir}/runSalome
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
cat > %{build_root}%{_bindir}/killSalome << EOF
#!/bin/sh

PIDS=\`ps x |
egrep '\<(notifd|SALOME_Session_Server|SALOME_LauncherServer|SALOME_ConnectionManagerServer|FactoryServerPy|omniNames)\>' |
grep -v egrep |
awk '{ print \$1; }'\`
[ -z "\$PIDS" ] || kill \$PIDS
EOF
chmod +x %{build_root}%{_bindir}/killSalome
#-----------------------------------------------------------------------

# some files in %py_puresitedir uses interfaces to load dynamic modules
# but want the files in the same directory, not %py_platsitedir
%ifarch x86_64 ppc64
  pushd %{build_root}%{py_puresitedir}
    mv -f %{name}/* %{build_root}%{py_platsitedir}/%{name}
    rmdir %{name}
  popd
%endif

rm -f %{build_root}%{py_platsitedir}/%{name}/*.a
mv -f %{build_root}%{_libdir}/%{name}/_libSALOME_Swig.* %{build_root}%{py_platsitedir}/%{name}
mv -f %{build_root}%{_bindir}/%{name}/libSALOME_Swig.py %{build_root}%{py_platsitedir}/%{name}

mkdir -p %{build_root}%{_datadir}/%{name}/samples
cp -far SAMPLES_SRC_%{version}/* %{build_root}%{_datadir}/%{name}/samples
cp -fa HXX2SALOMEDOC_SRC_%{version}/*  %{build_root}%{_docdir}/%{name}

install -m644 -D %{SOURCE3} %{build_root}%{_miconsdir}/%{name}.png
install -m644 -D %{SOURCE4} %{build_root}%{_iconsdir}/%{name}.png
install -m644 -D %{SOURCE4} %{build_root}%{_datadir}/pixmaps/%{name}.png
mkdir -p %{build_root}%{_datadir}/applications
cat > %{build_root}%{_datadir}/applications/mandriva-%{name}.desktop << EOF
[Desktop Entry]
Name=Salome
Comment=Pre- and Post-Processing for numerical simulation
Exec=runSalome
Icon=%{name}
Terminal=false
Type=Application
Categories=Science;Physics;
EOF

## This must (should?) be the last commands to update buildroot from
## installed files in build_root and work with any rpm version
rm -fr %{buildroot}/*
cp -fpar %{build_root}/* %{buildroot}

#-----------------------------------------------------------------------
%files
%defattr(-,root,root)
%{_bindir}/runSalome
%{_bindir}/killSalome
%dir %{_datadir}/idl/salome
%{_datadir}/idl/salome/*
%dir %{py_platsitedir}/%{name}
%{py_platsitedir}/%{name}/*
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/resources
%{_datadir}/%{name}/resources/*
%dir %{_datadir}/%{name}/salome_adm
%{_datadir}/%{name}/salome_adm/*
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%dir %{_docdir}/%{name}
%{_docdir}/%{name}/*
%dir %{_bindir}/%{name}
%{_bindir}/%{name}/*
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
