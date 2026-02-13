To configure the font size, you need to:

- Go to Settings / General Settings / Companies, and click on the 'Configure Document Layout' button
- Edit text size, text size unit, header size, and header size unit


To directly customize the report css (only recomended for developers), you need to

- Go to Settings / General Settings / Companies, and click on the 'Configure Document Layout' button
- Activate the developer mode
- Go to custom CSS, and write your css there.

Here you have a list of css code examples you can insert into the custom css.

Usefull css properties:

```
line-height: 1.5;
font-weight: 300;
margin: 0 100px;
color: blue;
```

Special css selectors. Some text blocks of the reports are not edited by normal css because they use special classes that overwrite the main css, you should use this special css selectors to edit those blocks:

```
h2 {
    color: blue;
}
#informations strong {
    color: blue;
}
table * {
    color: blue !important;
}
```

Finally, it can be usefull knowing that the font size fields of the form view create a css similar to the following one:

```
font-size: 16.0px;
h2 {
    font-size: 32.0px;
}
```
