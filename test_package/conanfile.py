from conans import ConanFile, CMake
import platform

class BlackmagicTestConan(ConanFile):
    requires = 'llvm/3.3-5@vuo/stable'
    generators = 'cmake'

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy('*', src='lib', dst='lib')

    def test(self):
        self.run('./bin/test_package')

        # Ensure we only link to system libraries and to libraries we built.
        if platform.system() == 'Darwin':
            self.run('! (otool -L lib/libblackmagic.dylib | tail +3 | egrep -v "^\s*(/usr/lib/|/System/|@rpath/)")')
            self.run('! (otool -L lib/libblackmagic.dylib | fgrep "libstdc++")')
            self.run('! (otool -L lib/libblackmagic.dylib | fgrep "@rpath/libc++.dylib")')  # Ensure this library references the system's libc++.
            self.run('! (otool -l lib/libblackmagic.dylib | grep -A2 LC_RPATH | cut -d"(" -f1 | grep "\s*path" | egrep -v "^\s*path @(executable|loader)_path")')
        elif platform.system() == 'Linux':
            self.run('! (ldd lib/libblackmagic.so | grep -v "^lib/" | grep "/" | egrep -v "(\s(/lib64/|(/usr)?/lib/x86_64-linux-gnu/)|test_package/build|/\.conan/data/)")')
            self.run('! (ldd lib/libblackmagic.so | fgrep "libstdc++")')
        else:
            raise Exception('Unknown platform "%s"' % platform.system())
