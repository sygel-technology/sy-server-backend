To use this module, you need to:

1.  Create a model that inherits from file.download.model.
2.  Override the following functions:
    - **\`get_filename\`**: Return the desired file name.

    - **\`get_content\`**: Return the binary string file to download.
      For example:

      ``` python
      from io import StringIO

      def get_content(self):
          output = StringIO()
          file.save(output)
          output.seek(0)
          return output.read()
      ```
3.  After this, create a wizard with a button that calls the function
    set_file. This function will open a new wizard with the downloadable
    file.
