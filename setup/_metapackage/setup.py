import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-sygel-technology-sy-server-backend",
    description="Meta package for sygel-technology-sy-server-backend Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-reports_font_size',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
