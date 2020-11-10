from conans import ConanFile, CMake, tools
import os
import platform

class BlackmagicConan(ConanFile):
    name = 'blackmagic'

    source_version = '11.6'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://www.blackmagicdesign.com/support/'
    description = 'Video capture and playback'
    generators = 'cmake'
    build_dir = '_build'
    exports_sources = 'CMakeLists.txt'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')

        if platform.system() == 'Darwin':
            pf = 'Mac'
            self.libext = 'dylib'
        elif platform.system() == 'Linux':
            pf = 'Linux'
            self.libext = 'so'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.platformDir = 'Blackmagic DeckLink SDK %s/%s' % (self.source_version, pf)

    def source(self):
        tools.mkdir('include')
        tools.mkdir('lib')
        tools.get('https://sw.blackmagicdesign.com/DeckLink/v11.6/Blackmagic_DeckLink_SDK_11.6.zip?Key-Pair-Id=APKAJTKA3ZJMJRQITVEA&Signature=bbLJJfKW8rXlPCA30sw0Q1N47ODcfmBkcVlK8KQ9ReWgSJ8NdGj118Lx5WgEB9Ee5oSWQp6y9Psk4lLT9dNF2GkTQFzFkcYMmr0RaCI6nINen3Hem1XkuwhFNsDCoDUsh8PCI0aVZ8QQoADGfhHe8Ui2HJtAjkFkybX1hXWc62V/3CaBSSU83Gtl1qWWSaXU1jDILnzdt0sQ619hXghGzuVP9rDim5GukzysrORgChJJv5Al2S7QUaAd/cPYweSm1Ms7Nr+qlOxzVnaXrn28NHBLNmgvTrCRiipxOlWBSp++mzHUFK/wOU/YgHrepNp7dRQ80q/6nxjKbvVafl8LPA==&Expires=1604983396',
            sha256='2cecde0b6af98ef3cefa425ec0595849fb30a26da4063becd80582dbc0483183',
            filename='sdk.zip')

        self.run('mv "%s/include"/*.h include' % self.platformDir)
        # Exclude older header versions.
        self.run('rm include/*_v[0-9]*.h')

    def build(self):
        cmake = CMake(self)
        cmake.definitions['CONAN_DISABLE_CHECK_COMPILER'] = True
        cmake.definitions['CMAKE_BUILD_TYPE'] = 'Release'
        cmake.definitions['CMAKE_C_COMPILER'] = '%s/bin/clang' % self.deps_cpp_info['llvm'].rootpath
        cmake.definitions['CMAKE_C_FLAGS'] = '-Oz'
        cmake.definitions['CMAKE_SKIP_BUILD_RPATH'] = True
        cmake.definitions['CMAKE_BUILD_WITH_INSTALL_NAME_DIR'] = True
        cmake.definitions['CMAKE_INSTALL_NAME_DIR'] = '@rpath'
        cmake.definitions['CMAKE_OSX_ARCHITECTURES'] = 'x86_64;arm64'
        cmake.definitions['CMAKE_OSX_DEPLOYMENT_TARGET'] = '10.11'
        cmake.definitions['CMAKE_OSX_SYSROOT'] = self.deps_cpp_info['macos-sdk'].rootpath
        cmake.definitions['BLACKMAGIC_SDK_DIR'] = self.platformDir

        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            cmake.configure(source_dir='..', build_dir='.', args=['--no-warn-unused-cli'])
            cmake.build()
            self.run('install_name_tool -change @rpath/libc++.dylib /usr/lib/libc++.1.dylib lib/libblackmagic.dylib')

    def package(self):
        self.copy('*.h', src='include', dst='include')
        self.copy('libblackmagic.%s' % self.libext, src='%s/lib' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['blackmagic']
