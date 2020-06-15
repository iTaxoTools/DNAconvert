# Internal tab format
A format representing genetic information in tab-separated values form

## Description
First line is a tab-separated list of field names. Names 'uniquesequencename' and 'sequence' are required.

Other lines are a tab-separated lists of field values.
Number of values in a line should be equal to the number of fields' names in the first line.
A value can be an empty string, but the number of tab symbols in each line should be exactly the same.
Empty lines are allowed and ignored during reading.
