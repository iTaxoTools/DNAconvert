from typing import Optional


class Record:
    """Class for records with a smart constructor that guarantees the presence of required fields
    """

    def __init__(self, **kwargs: str):
        """Creates a record with given fields
        Raises an ValueError if a requred field is not supplied

        Field 'sequence' is required, as at least one other field
        """
        if len(kwargs) < 2:
            raise ValueError("The input has less than 2 fields")
        if 'sequence' not in kwargs:
            raise ValueError("field 'sequence' is required")
        self._fields = kwargs

    def __getitem__(self, field: str) -> str:
        """r.__getitem__(field) <==> r[field]
        """
        return self._fields[field]

    def __setitem__(self, field: str, value: str) -> None:
        """Sets self[field] to a value
        """
        self._fields[field] = value

    def get(self, field: str) -> Optional[str]:
        """
        returns the value of the field
        returns None if it doesn't exists
        """
        return self._fields.get(field)
