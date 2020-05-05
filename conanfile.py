from conans import ConanFile, tools
import platform

class BlackmagicConan(ConanFile):
    name = 'blackmagic'

    source_version = '11.5.1'
    package_version = '0'
    version = '%s-%s' % (source_version, package_version)

    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'https://www.blackmagicdesign.com/support/'
    description = 'Video capture and playback'
    build_dir = '_build'

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')

        if platform.system() == 'Darwin':
            pf = 'Mac'
        elif platform.system() == 'Linux':
            pf = 'Linux'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        self.platformDir = 'Blackmagic DeckLink SDK %s/%s' % (self.source_version, pf)

    def source(self):
        tools.mkdir('include')
        tools.mkdir('lib')
        tools.get('https://sw.blackmagicdesign.com/DeckLink/v11.5.1/Blackmagic_DeckLink_SDK_11.5.1.zip?Key-Pair-Id=APKAJTKA3ZJMJRQITVEA&Signature=GffCQRr6q9FjZnk8uCMID5R31dsiCNGbh8w5mmy+XtDDQ+m+c5BM/hT0Yv6wE+6+1EMFq7l5RX0YTE1q1rsQaQzt1IP0C406Iu7FHlZT07yXF8A0d0HqZLJOvtrL4Z+Gxv29YetRUnUq3ijNKD6JsxisAvDLccbje1ekj7Dsv58H+FYqcFZbp+0OevpZnkfhBWB/C6hf9phtXmoV64292xxekn7VMlzJmDbNT2DAygRkryaXNeP4v8uTvD+yW7unX1ftf2xYMIJizFeI7G7o8Hsky0QKDg9DIXzyDXNWRMKQYQRGI5/3EPG3xXto8ILkDU5Vg9jy70Jo66IRG4uw7A==&Expires=1588731623',
            sha256='60df0abb766c724c5c60cd44f1ff9715725ed79ee0a8e3ffef34c4d24ba5811f',
            filename='sdk.zip')

        self.run('mv "%s/include"/*.h include' % self.platformDir)
        # Exclude older header versions.
        self.run('rm include/*_v[0-9]*.h')

    def build(self):
        if platform.system() == 'Darwin':
            self.libext = 'dylib'
            platformBuild = '-dynamiclib -framework CoreFoundation -isysroot /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk -mmacosx-version-min=10.10'
        elif platform.system() == 'Linux':
            self.libext = 'so'
            platformBuild = '-shared -fPIC -lpthread -ldl'
        else:
            raise Exception('Unknown platform "%s"' % platform.system())

        tools.mkdir(self.build_dir)
        with tools.chdir(self.build_dir):
            self.run('clang++ -oz "../%s/include"/DeckLinkAPIDispatch.cpp -I"../include" %s -stdlib=libc++ -install_name @rpath/libblackmagic.%s -o libblackmagic.%s' % (self.platformDir, platformBuild, self.libext, self.libext))

    def package(self):
        self.copy('*.h', src='include', dst='include')
        self.copy('libblackmagic.%s' % self.libext, src='%s' % self.build_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['blackmagic']
