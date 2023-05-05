from setuptools import setup, find_packages

from setuptools.command.build_py import build_py

class install_py(build_py):
    def run(self) -> None:
        # do somethis here
        print("INSTALLING [ CHARGE SLIP VALIDATOR ] for Ezetap..")

        super().run()



setup(
    name='charge_slip_validator',
    version='0.1.0',    
    description='This library will initialise the working directory as a package that can be installed by pip',
    url='https://github.com/santokalayil/py_package_maker',
    author='Santo K Thomas',
    author_email='santokalayil@gmail.com',
    license='MIT',
    # packages=['charge_slip_validator', 'charge_slip_validator.errors'],
    packages=find_packages(
        include=(
            'charge_slip_validator',
            'charge_slip_validator.*', 
            'charge_slip_validator.errors.*',
        )
    ),
    install_requires=[
        'setuptools', 'jinja2>=3.1.0', 'opencv-python', 'numpy', 'matplotlib',
        'pyyaml', 'imutils', 'selenium', 'geckodriver-autoinstaller',
    ],

    cmdclass={'build_py': install_py},

    # this is to include datafiles listed in the MANIFEST.in  file
    # include_package_data=True,
    package_data={
        'charge_slip_validator': [
            'assets/configuration.yaml',
            # 'media/.*',
            'assets/media/logos/manual_references/*.png',
            'assets/media/logos/ideal_references/*',
            'assets/media/screenshots/original/*.png',
            'assets/media/screenshots/cropped/*.png',
            'assets/media/screenshots/padded/*.png',
            
        ]
    },


    classifiers=[
        'License :: OSI Approved :: MIT License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)

