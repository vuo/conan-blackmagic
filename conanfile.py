from conans import ConanFile, CMake, tools
import os
import platform

class BlackmagicConan(ConanFile):
    name = 'blackmagic'

    source_version = '12.0'
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

        self.platformDir = 'Blackmagic DeckLink SDK 12.0/%s' % pf

    def source(self):
        tools.mkdir('include')
        tools.mkdir('lib')
        tools.get('https://sw.blackmagicdesign.com/DeckLink/v12.0/Blackmagic_DeckLink_SDK_12.0.zip?Key-Pair-Id=APKAJTKA3ZJMJRQITVEA&Signature=NNP8rztcVRymb8dLddJqX3J4+SZ4d0i4FH1G9tt58W2BnCnKH6OLxxKCZByNH6kG7KC2V+7Sdl2yCFVonz1673qFBjnwwFNXboEz/8yn7s/mMa6t9GFdw7+Fjc9n3VG1inT0aPpfPc92A/XnAMlbzHeAmrnF6jdmQAo/++TpIZ4aRHI7ypqcRJ77hPopi32HzrjTwxzxVqcU4nKPZR1ErFtPIbUenozZLM6MdcqkDNElvqyXIwLfczNgVhvwuZutF+3Z2Vwq4K1etTyYPprWeuU3LBsH6SbO3QLUr4/pp/s/MzUIOWB5Kc2BN5F/jllM1Tw5JghHQ7Bd6TWefl/2Kw==&Expires=1611438177',
            sha256='89b34b05ae1fbe209129de767606300583bcce4266d9476293a43fe2e881fcf5',
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
