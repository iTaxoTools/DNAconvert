# Adding additional formats
To add a capacity to read and write additional formats, you need to create a read-write module for the format and add information about it
into `lib/formats.py`

## Read-write module
This module should contains a class, corresponding to the format, with two static methods `read` and `write` with following signatures:
```python
class MyFormat:
    @staticmethod
    def write(file, fields)
    @staticmethod
    def read(file)
```

The `write` method receives an output file `file` and a list of fields `fields`. It should be a generator that receives object of
class `Record` and writes them to the file `file` according to the format being implemented.
Each `Record` can be expected to contain all the fields in the list `fields`.
The method is not expected to return anything. **It must not mutate the `fields` parameter!**.
Can raise `ValueError`, if `fields` doesn't contain a required field.

The `read` method receives an input file `file`. It should return a list of fields and a generator. The generator should
yield one-by-one objects of class `Record`, which together contain all the relevant information in the file. Each `Record` must contain at
least all the fields named in the list. Can raise `ValueError`, if the file cannot be parsed.

## Registering the format
In the file `lib\formats.py`
1) Import the module
2) Add a key-value pair `'format name': 'format class'` to the `formats` dictionary
3) (Optionally) Add a key-value pair `'extension': 'format class'` to the `extensions` dictionary. `'extension'` must start with a period.

## The Record class
`lib\record.py` define a `Record` class, that should emitted by `read` and consumed by `write`. It's a wrapper around a dictionary, with the constructor that requires the field `'sequence'` and at least one other field to be present. Example:
```python
Record(uniquesequencename='sequencename', location='Madagascar', sequence='ATGC')
```
If the required fields are not present, a `ValueError` will be raised.

`Record` implements `__getitem__` and `__setitem__` methods.
