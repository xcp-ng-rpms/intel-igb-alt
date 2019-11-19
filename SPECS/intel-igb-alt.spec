%define vendor_name Intel
%define vendor_label intel
%define driver_name igb
%define vf_param max_vfs
%define vf_maxvfs 7

# XCP-ng: we need this short version without any "+..." part
# because override statements in /etc/depmod.d don't work with e.g. 4.4.0+10
%define kernel_version_short %(echo %kernel_version | sed 's/\+.*//')

# XCP-ng: install to the override directory
%define module_dir override

Summary: %{vendor_name} %{driver_name} device drivers
Name: %{vendor_label}-%{driver_name}-alt
Version: 5.3.5.39
Release: 1%{?dist}
License: GPL

# Downloaded from https://downloadcenter.intel.com/download/13663/Intel-Network-Adapter-Driver-for-82575-6-82580-I350-and-I210-211-Based-Gigabit-Network-Connections-for-Linux-
Source0: igb-%{version}.tar.gz

BuildRequires: gcc
BuildRequires: kernel-devel
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

# XCP-ng: for /etc/modprobe.d/igb.conf
Requires: intel-igb

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1 -n igb-%{version}

%build
%{?cov_wrap} %{make_build} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src KSRC=/lib/modules/%{kernel_version}/build modules

%install
# XCP-ng: we don't create /etc/modprobe.d/igb.conf here since the intel-igb package
# already provides it
#%{__install} -d %{buildroot}%{_sysconfdir}/modprobe.d
#echo '# VFs-param: %{vf_param}' > %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
#echo '# VFs-maxvfs-by-default: %{vf_maxvfs}' >> %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
#echo '# VFs-maxvfs-by-user:' >> %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
#echo 'options %{driver_name} %{vf_param}=0' >> %{buildroot}%{_sysconfdir}/modprobe.d/%{driver_name}.conf
%{?cov_wrap} %{__make} %{?_smp_mflags} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=%{module_dir} DEPMOD=/bin/true modules_install

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

# XCP-ng: override depmod configuration to give priority to our alternative driver
mkdir -p %{buildroot}/etc/depmod.d
echo "override %{module_name} %{kernel_version_short} %{module_dir}" > %{buildroot}/etc/depmod.d/%{module_name}-%{kernel_version_short}.conf

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
/lib/modules/%{kernel_version}/*/*.ko
/etc/depmod.d/%{module_name}-%{kernel_version_short}.conf

%changelog
* Tue Nov 19 2019 Samuel Verschelde <stormi-xcp@ylix.fr> - 5.3.5.39-1
- Update to 5.3.5.39
- Initial package
