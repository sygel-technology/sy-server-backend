- More css units can be added.

- The _get_asset_style_b64() call when updating the web.asset_styles_company_report attachment has been overwritten, replacing it for _custom_get_asset_style_b64(). The reason is that, without this change, a update of the base module deletes the css injection. Modules that inherits the _get_asset_style_b64 function might be incompatible. This was the only way found to fix this issue.

- If a report uses special custom classes, the font size could not be changed. It is not common, but it has been detected that it happens with the boxed reports in v16. It can also happen if a report uses headers other than h2. If this happens to you, tell the technician who creates CSS for you. Example to solve the size of headers 1, and the direction of the boxed:

  ```
  font-size: 20px;
  h1 {
      font-size: 40px;
  }
  .o_boxed_header {
      font-size: 20px;
  }
  ```
