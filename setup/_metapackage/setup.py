import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-sygel-technology-sy-server-backend",
    description="Meta package for sygel-technology-sy-server-backend Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-easy_massive_translation',
        'odoo13-addon-mail_show_follower',
        'odoo13-addon-reports_font_size',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
