
If a report uses special custom classes, the font size cannot be changed. It is not common, but it has been detected that it happens with the direction of boxed reports. It can also happen if a report uses headers other than h2. If this happens to you, tell the technician who creates CSS for you. Example to solve the size of headers 1, and the direction of the boxed:

font-size: 20px;
h1 {
    font-size: 40px;
}
.o_boxed_header {
    font-size: 20px;
}


Migrations between v15 y v18 should de fast and easy.

More css units can be added.
