from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
import sys, os, glob
import setuptools

__version__ = '0.2.0'


class get_pybind_include(object):
    """Helper class to determine the pybind11 include path
    The purpose of this class is to postpone importing pybind11
    until it is actually installed, so that the ``get_include()``
    method can be invoked. """

    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)

include_dirs = [
    # Path to pybind11 headers
    './include/',
    get_pybind_include(),
    get_pybind_include(user=True)
]

library_dirs = None
cgal_libs = ["CGAL", "CGAL_Core"]

if os.getenv('CONDA_PREFIX') or os.getenv('MINICONDAPATH'):

    if sys.platform.startswith('win'):
        prefix = os.path.join(sys.prefix, 'Library\\')
    else:
        prefix = sys.prefix

    print("Looking for CGAL in: ", prefix)

    extra_link_args = []
    if sys.platform == 'darwin':
        extra_link_args = ['-Wl,-rpath', '-Wl,%s' % os.path.abspath(prefix)]


    if sys.platform == 'win32':
        library_dir = os.path.join(prefix, 'lib')
        # currently we also need to add the apparently windows specific suffix here, it's unclear if this is 
        # necessary if CGAL is installed not from CONDA.
        # suffix = "-vc140-mt-4.14.1"
        adjusted_cgal_libs = []
        for lib in cgal_libs:
            candidates = glob.glob(os.path.join(library_dir, lib) + '*.lib')
            if not candidates:
                raise RuntimeError("Library not found [[{}]]".format(lib))
            c = os.path.basename(candidates[0])
            c = os.path.splitext(c)[0]
            adjusted_cgal_libs.append(c)
        cgal_libs = adjusted_cgal_libs

        library_dirs = [library_dir]
        print("Looking for CGAL library in ", library_dirs)
        print("Names of adjusted CGAL libs: ", adjusted_cgal_libs)

    include_dirs.insert(1, os.path.join(prefix, 'include'))

ext_modules = [
    Extension(
        'skgeom._skgeom',
        [
            'src/skgeom.cpp',
            'src/kernel.cpp',
            'src/polygon.cpp',
            'src/global_functions.cpp',
            'src/boolean.cpp',
            'src/convex_hull.cpp',
            'src/visibility.cpp',
            'src/arrangement.cpp',
            'src/principal_component_analysis.cpp',
            'src/minkowski.cpp',
            'src/polyhedron.cpp',
            'src/aabb_tree.cpp',
            'src/voronoi_delaunay.cpp',
            'src/optimal_transport.cpp'
        ],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=cgal_libs + ['mpfr',
                   'gmp', 
                   'boost_thread',
                   'boost_atomic',
                   'boost_system',
                   'boost_date_time',
                   'boost_chrono'],
        language='c++'
    ),
]


# As of Python 3.6, CCompiler has a `has_flag` method.
# cf http://bugs.python.org/issue26689
def has_flag(compiler, flagname):
    """Return a boolean indicating whether a flag name is supported on
    the specified compiler.
    """
    import tempfile
    with tempfile.NamedTemporaryFile('w', suffix='.cpp') as f:
        f.write('int main (int argc, char **argv) { return 0; }')
        try:
            compiler.compile([f.name], extra_postargs=[flagname])
        except setuptools.distutils.errors.CompileError:
            return False
    return True


def cpp_flag(compiler):
    """Return the -std=c++[11/14/17] compiler flag.
    The newer version is prefered over c++11 (when it is available).
    """
    flags = ['-std=c++17', '-std=c++14', '-std=c++11']

    for flag in flags:
        if has_flag(compiler, flag): return flag

    raise RuntimeError('Unsupported compiler -- at least C++11 support '
                       'is needed!')


class BuildExt(build_ext):
    """A custom build extension for adding compiler-specific options."""
    c_opts = {
        'msvc': ['/EHsc', '/std:c++14'],
        'unix': [],
    }
    l_opts = {
        'msvc': [],
        'unix': [],
    }

    if sys.platform == 'darwin':
        darwin_opts = ['-stdlib=libc++', '-mmacosx-version-min=10.12']
        c_opts['unix'] += darwin_opts
        l_opts['unix'] += darwin_opts

    def initialize_options(self):
        super(BuildExt, self).initialize_options()
        self.debug = False
        self.parallel = True

    def build_extensions(self):
        ct = self.compiler.compiler_type
        opts = self.c_opts.get(ct, [])
        link_opts = self.l_opts.get(ct, [])
        if ct == 'unix':
            opts.append('-DVERSION_INFO="%s"' % self.distribution.get_version())
            opts.append(cpp_flag(self.compiler))
            if has_flag(self.compiler, '-fvisibility=hidden'):
                opts.append('-fvisibility=hidden')
        elif ct == 'msvc':
            opts.append('/DVERSION_INFO=\\"%s\\"' % self.distribution.get_version())
        for ext in self.extensions:
            ext.extra_compile_args = opts
            ext.extra_link_args = link_opts

        build_ext.build_extensions(self)

setup(
    name='skgeom',
    version=__version__,
    author='Wolf Vollprecht',
    author_email='w.vollprecht@gmail.com',
    url='https://github.com/wolfv/scikit-geometry',
    description='scikit-geometry, the python computational geometry library',
    long_description='',
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.3'],
    setup_requires=['pybind11>=2.3'],
    cmdclass={'build_ext': BuildExt},
    zip_safe=False,
)
