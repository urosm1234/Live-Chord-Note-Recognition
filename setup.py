from setuptools import setup, Extension
import numpy

# Extension module definition
ext_modules = [
    Extension(
        'CQTransform',
        ['CQTransform.cpp'],
        include_dirs=[numpy.get_include()],
        libraries=[],
        library_dirs=[],
        extra_compile_args=['-O3'],
    ),
]

setup(
    name='CQTransform',
    version='0.1',
    ext_modules=ext_modules,
    zip_safe=False,
)