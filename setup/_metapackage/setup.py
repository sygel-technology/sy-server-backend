import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-sygel-technology-sy-server-backend",
    description="Meta package for sygel-technology-sy-server-backend Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-base_old_migration_fields>=16.0dev,<16.1dev',
        'odoo-addon-file_download>=16.0dev,<16.1dev',
        'odoo-addon-odoo_2_odoo_data_transfer>=16.0dev,<16.1dev',
        'odoo-addon-reports_font_size>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
