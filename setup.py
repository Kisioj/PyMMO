import setuptools

with open("README.md", "r", encoding="utf-8") as readme:
    LONG_DESCRIPTION = readme.read()

setuptools.setup(
    name='pymmo',
    version='0.0.1',
    license='LGPLv3',
    url='https://pymmo.com',
    author='Krzysztof Jura',
    author_email='kisioj@gmail.com',
    description='Python Online Game Development',

    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",

    project_urls={
        "Bug Tracker": "https://github.com/kisioj/PyMMO/issues",
        "Source": "https://github.com/kisioj/PyMMO",
    },

    install_requires=[
        'pyside6',
        'numpy',
        'PyOpenGL',
        'PyOpenGL_accelerate',
        'PyGLM',
        'Pillow',
    ],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.6',

    entry_points={
      'console_scripts': [
          'pymmo-admin=pymmo.core.management:run_command'
      ]
    },

    packages=[
        'pymmo',

        'pymmo.base_types',
        'pymmo.base_types.mappable',
        'pymmo.base_types.mappable.movable',

        'pymmo.interface',

        'pymmo.render',

        'pymmo.core',
        'pymmo.core.management',
        'pymmo.core.management.commands',
    ],
)
