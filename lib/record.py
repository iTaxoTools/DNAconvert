class Record:
    """Class for records with a smart constructor that guarantees the presence of required fields
    """
    def __init__(self, **kwargs):
        """Creates a record with given fields
        Raises an ValueError if a requred field is not supplied

        Required fields: 'uniquesequencename', 'sequence'
        """
        for required_field in ['uniquesequencename', 'sequence']:
            if required_field not in kwargs:
                raise ValueError(f"field '{required_field}' is required")
        self._fields = kwargs

    def __getitem__(self, field):
        """r.__getitem__(field) ~ r[field
        """
        return self._fields[field]
