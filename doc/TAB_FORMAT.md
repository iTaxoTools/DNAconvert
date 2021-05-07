# Internal tab format
A format representing genetic information in tab-separated values form

## Description
First line is a tab-separated list of field names. A name containing 'sequence' and at least one other name is expected.

Other lines are a tab-separated lists of field values.
Number of values in a line should be equal to the number of fields' names in the first line.
A value can be an empty string, but the number of tab symbols in each line should be exactly the same.
Empty lines are allowed and ignored during reading.

## Variant without the header line

`DNAconvert` uses the first line to detect the sequence column. By default it's the last column. 
If the last column contains unusual characters, the first column is chosen as the sequence column.

Each line is transformed into a list of non-empty tab-separated strings. The sequence string is yielded unchanged. The other strings are concatenated into the `seqid` value.

