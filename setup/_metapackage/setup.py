import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-sygel-technology-sy-server-backend",
    description="Meta package for sygel-technology-sy-server-backend Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-add_external_id',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 11.0',
    ]
)
