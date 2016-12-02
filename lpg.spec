%{?scl:%scl_package lpg}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

%global baserelease 3

%global    _version 2.0.17
%global    _compat_version 1.1.0

Name:      %{?scl_prefix}lpg
Version:   %{_version}
Release:   19.%{baserelease}%{?dist}
Summary:   LALR Parser Generator
# although the text of the licence isn't distributed with some of the source,
# the author has exlicitly stated that everything is covered under the EPL
# see: http://sourceforge.net/forum/forum.php?thread_id=3277926&forum_id=523519
License:   EPL
URL:       http://lpg.sourceforge.net/

Source0:   http://downloads.sourceforge.net/lpg/lpg-java-runtime-src-%{version}.zip
Source1:   http://downloads.sourceforge.net/lpg/lpg-generator-cpp-src-%{version}.zip
Source2:   http://downloads.sourceforge.net/lpg/lpg-generator-templates-%{version}.zip

# source archive for the java compat lib
Source3:   http://downloads.sourceforge.net/lpg/lpgdistribution-05-16-06.zip

# upstream does not provide a build script or manifest file for the java
# compat lib
Source4:   %{pkg_name}-build.xml
Source5:   %{pkg_name}-manifest.mf

# TODO: drop Source3, 4, 5 and obsolete the java-compat package when dependent
# projects are ported to LPG 2.x.x

# executable name in the bootstrap make target is wrong; sent upstream, see:
# https://sourceforge.net/tracker/?func=detail&aid=2794057&group_id=155963&atid=797881
Patch0:    %{pkg_name}-bootstrap-target.patch

# change build script to build the base jar with osgi bundle info
Patch1:    %{pkg_name}-osgi-jar.patch

# fix segfault caused by aggressive optimisation of null checks in gcc 4.9
Patch2:    %{pkg_name}-segfault.patch

%description
The LALR Parser Generator (LPG) is a tool for developing scanners and parsers
written in Java, C++ or C. Input is specified by BNF rules. LPG supports
backtracking (to resolve ambiguity), automatic AST generation and grammar
inheritance.

%package       java
Summary:       Java runtime library for LPG

BuildArch:     noarch
Provides:      %{?scl_prefix}osgi(lpg.runtime.java) = 2.0.17

BuildRequires: %{?scl_prefix_java_common}jpackage-utils
BuildRequires: %{?scl_prefix_java_common}ant-apache-regexp

Requires:      %{?scl_prefix_java_common}jpackage-utils
Requires:      %{?scl_prefix}runtime

%description   java
Java runtime library for parsers generated with the LALR Parser Generator
(LPG).

%package       java-compat
Version:       %{_compat_version}
Summary:       Compatibility Java runtime library for LPG 1.x

BuildArch:     noarch
Provides:      %{?scl_prefix}osgi(net.sourceforge.lpg.lpgjavaruntime) = 1.1.0

BuildRequires: %{?scl_prefix_java_common}jpackage-utils
BuildRequires: %{?scl_prefix_java_common}ant

Requires:      %{?scl_prefix_java_common}jpackage-utils
Requires:      %{?scl_prefix}runtime

%description   java-compat
Compatibility Java runtime library for parsers generated with the LALR Parser
Generator (LPG) 1.x.

%prep
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
%setup -q -T -c -n %{pkg_name}-%{version}

# because you can't use setup to unzip to subdirectories when your source
# archives do not create top level directories
unzip -qq %{SOURCE0} -d lpg-java-runtime
unzip -qq %{SOURCE1} -d lpg-generator-cpp
unzip -qq %{SOURCE2} -d lpg-generator-templates
chmod -Rf a+rX,u+w,g-w,o-w .

# setup java compat stuff
%setup -q -D -T -a 3 -n %{pkg_name}-%{version}
cp -p %{SOURCE4} lpgdistribution/build.xml
cp -p %{SOURCE5} lpgdistribution/MANIFEST.MF

# apply patches
%patch0 -p0 -b .orig
%patch1 -p0 -b .orig
%patch2 -p0 -b .orig
%{?scl:EOF}


%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
# build java stuff
(cd lpg-java-runtime && ant -f exportPlugin.xml)

# build java compat stuff
(cd lpgdistribution && ant)

# build native stuff
pushd lpg-generator-cpp/src

# ARCH just tells us what tools to use, so this can be the same on all arches
# we build twice in order to bootstrap the grammar parser
make clean install ARCH=linux_x86 \
  LOCAL_CFLAGS="%{optflags} -Wno-strict-overflow" LOCAL_CXXFLAGS="%{optflags} -Wno-strict-overflow"
make bootstrap ARCH=linux_x86
make clean install ARCH=linux_x86 \
  LOCAL_CFLAGS="%{optflags} -Wno-strict-overflow" LOCAL_CXXFLAGS="%{optflags} -Wno-strict-overflow"

popd
%{?scl:EOF}


%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
set -e -x
install -pD -T lpg-java-runtime/%{pkg_name}runtime.jar \
  %{buildroot}%{_javadir}/%{pkg_name}runtime.jar
install -pD -T lpgdistribution/%{pkg_name}javaruntime.jar \
  %{buildroot}%{_javadir}/%{pkg_name}javaruntime.jar
install -pD -T lpg-generator-cpp/bin/%{pkg_name}-linux_x86 \
  %{buildroot}%{_bindir}/%{pkg_name}
%{?scl:EOF}


%files
%doc lpg-generator-templates/docs/*
%{_bindir}/%{pkg_name}

%files java
%doc lpg-java-runtime/Eclipse*.htm
%{_javadir}/%{pkg_name}runtime.jar

%files java-compat
%doc lpg-java-runtime/Eclipse*.htm
%{_javadir}/%{pkg_name}javaruntime.jar

%changelog
* Fri Aug 12 2016 Mat Booth <mat.booth@redhat.com> - 2.0.17-19.3
- Ensure package requires SCL runtime

* Thu Jul 21 2016 Mat Booth <mat.booth@redhat.com> - 2.0.17-19.2
- Add missing osgi provides

* Thu Jul 21 2016 Mat Booth <mat.booth@redhat.com> - 2.0.17-19.1
- Auto SCL-ise package for rh-eclipse46 collection

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.17-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jul 10 2015 Mat Booth <mat.booth@redhat.com> - 2.0.17-18
- Add Wno-strict-overflow flag to remove unnecessary warning about subtracting
  one from an index value.

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat May 02 2015 Kalev Lember <kalevlember@gmail.com> - 2.0.17-16
- Rebuilt for GCC 5 C++11 ABI change

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jun 16 2014 Mat Booth <mat.booth@redhat.com> - 2.0.17-14
- Patch to fix segfault caused by aggressive optimisation of null checks in gcc 4.9

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Mar 11 2014 Mat Booth <fedora@matbooth.co.uk> - 2.0.17-12
- Drop versioned jars and switch to R: java-headless
  RHBZ #1068378 and #1022141

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Sat Feb 16 2013 Mat Booth <fedora@matbooth.co.uk> - 2.0.17-10
- Fix rpm %%doc parsing by globbing instead of escaping.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-9.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-8.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-7.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-6.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Oct 05 2010 jkeating - 2.0.17-5.1
- Rebuilt for gcc bug 634757

* Mon Sep 13 2010 Mat Booth <fedora@matbooth.co.uk> 2.0.17-5
- Re-patch the OSGi manifest because for some reason Eclipse Orbit decided
  not to use the same symbolic bundle name as LPG upstream did.

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.17-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 15 2009 Mat Booth <fedora@matbooth.co.uk> 2.0.17-3
- Add missing build dependency on ant-apache-regexp.
- Remove empty sub-package that was accidentally left.

* Sun Jul 05 2009 Mat Booth <fedora@matbooth.co.uk> 2.0.17-2
- Add version constants so we get the correct version numbers on the java
  libraries.

* Sat Jul 04 2009 Mat Booth <fedora@matbooth.co.uk> 2.0.17-1
- Update to 2.0.17.
- Add OSGI manifest info to the runtime jar.
- Bundle generator docs with the generator in the main package.

* Tue May 19 2009 Mat Booth <fedora@matbooth.co.uk> 2.0.16-2
- Better document source files/patches.

* Tue Apr 28 2009 Mat Booth <fedora@matbooth.co.uk> 2.0.16-1
- Initial release of version 2.
