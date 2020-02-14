from distutils.core import setup

setup(
    name='collaborative-platform',
    version='1',
    packages=['apps', 'apps.core', 'apps.core.migrations', 'apps.api_vis', 'apps.api_vis.migrations', 'apps.projects',
              'apps.projects.migrations', 'apps.close_reading', 'apps.close_reading.migrations', 'apps.vis_dashboard',
              'apps.vis_dashboard.migrations', 'apps.files_management', 'apps.files_management.migrations',
              'apps.files_management.file_conversions', 'collaborative_platform'],
    package_dir={'': 'src/collaborative_platform'},
    url='',
    license='',
    author='providedh',
    author_email='',
    description=''
)
