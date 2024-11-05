import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-sygel-technology-sy-server-backend",
    description="Meta package for sygel-technology-sy-server-backend Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-base_old_migration_fields>=15.0dev,<15.1dev',
        'odoo-addon-file_download>=15.0dev,<15.1dev',
        'odoo-addon-html_fields_document_layout_configuration>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
