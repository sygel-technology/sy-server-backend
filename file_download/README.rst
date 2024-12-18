.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=============
File Download
=============

This module lets you call a wizard to download any file.

Installation
============

To install this module, you need to:

1. Install it as usual via Odoo Apps or your preferred method.

Configuration
=============

No additional configuration is required for this module.

Usage
=====

To use this module, you need to:

1. Create a model that inherits from `file.download.model`.
2. Override the following functions:
   
   - **`get_filename`**: Return the desired file name.
   - **`get_content`**: Return the binary string file to download. For example:
     
     .. code-block:: python

        from io import StringIO

        def get_content(self):
            output = StringIO()
            file.save(output)
            output.seek(0)
            return output.read()

3. After this, create a wizard with a button that calls the function `set_file`.  
   This function will open a new wizard with the downloadable file.

Bug Tracker
===========

Bugs and errors are managed in `issues of GitHub <https://github.com/sygel-technology/sy-server-backend/issues>`_.  
In case of problems, please check if your issue has already been reported.  
If you are the first to discover it, help us by providing a detailed description  
`here <https://github.com/sygel-technology/sy-server-backend/issues/new>`_.

Please do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* Sygel, Odoo Community Association (OCA)

Contributors
------------

* Valentin Vinagre <valentin.vinagre@sygel.es>
* Ángel García de la Chica Herrera <angel.garcia@sygel.es>

Maintainer
----------

This module is maintained by Sygel.

.. image:: https://www.sygel.es/logo.png
   :alt: Sygel
   :target: https://www.sygel.es

This module is part of the `Sygel/sy-server-backend <https://github.com/sygel-technology/sy-server-backend>`_.  

To contribute to this module, please visit https://github.com/sygel-technology.
