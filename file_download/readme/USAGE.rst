To use this module, you need to:

#. Create a model that inherits from `file.download.model`.
#. Override the following functions:
   
   - **`get_filename`**: Return the desired file name.
   - **`get_content`**: Return the binary string file to download. For example:
     
     .. code-block:: python

        from io import StringIO

        def get_content(self):
            output = StringIO()
            file.save(output)
            output.seek(0)
            return output.read()

#. After this, create a wizard with a button that calls the function `set_file`.  
   This function will open a new wizard with the downloadable file.
