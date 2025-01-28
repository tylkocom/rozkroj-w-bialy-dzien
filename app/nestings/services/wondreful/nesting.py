import abc
import io
import zipfile
from collections import defaultdict, Counter

from nestings.serializers import Element
from nestings.types import RowFlat

SHELF_TYPES_SHORTCUTS = {
    0: 'T1',
    1: 'T2',
}


class BaseNesting(abc.ABC):
    excluded_elements: list
    filename: str

    def __init__(self, product):
        self.product = product
        self.filenames_with_rows = defaultdict(list)
        self._save_rows()

    def __call__(self, **kwargs) -> tuple[str, bytes]:
        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zip_object:
            for filename, rows in self.filenames_with_rows.items():
                nesting_file = self.get_file(rows)
                zip_object.writestr(f'{filename}', nesting_file)
        zip_output.seek(0)
        return self.filename, zip_output.getvalue()

    def _save_rows(self) -> None:
        for  element in self.product.elements:
            if self._is_element_excluded(element):
                continue
            self._save_row(element)

    def _save_row(
        self,
        element: Element,
    ) -> None:
        """
        Writes a line with an element.
        """
        filename = self.get_filename_for_element(element)
        row = self.get_row(element)
        self.filenames_with_rows[filename].append(row)

    def _is_element_excluded(self, element: Element) -> bool:
        element_type = element.type
        return element_type in self.excluded_elements

    @abc.abstractmethod
    def get_filename_for_element(self, element: Element) -> str:
        """Returns the name of the nesting file for a specific element."""

    @abc.abstractmethod
    def get_row(
        self,
        element: Element,
    ) -> RowFlat:
        """Returns single row for file."""

    @abc.abstractmethod
    def get_file(self, rows: list) -> str:
        """Returns file generated from rows with row count."""


class WondrefulNesting(BaseNesting):
    excluded_elements = ['door', 'drawer']
    filename = 'wondreful_nesting.zip'

    def get_filename_for_element(self, element: Element) -> str:
        return f'{element.name}.csv'

    def get_row(
        self,
        element: Element,
    ) -> RowFlat:
        count = Counter()
        for product_element in self.product.elements:
            count[product_element.elem_type] += 1
        return (
            count[element.elem_type],
            element.name,
            element.pack_id,
            element.elem_type,
            element.material,
        )

    def get_file(self, rows: list) -> str:
        output = io.StringIO()
        output.write('count;name;pack_id;elem_type;material\n')
        for row in rows:
            output.write(f'{";".join(str(val) for val in row)}\n')
        return output.getvalue()


class WondrefulNewNesting(WondrefulNesting):
    filename = 'wondreful_new_nesting.zip'

    def get_row(
        self,
        element: Element,
    ) -> RowFlat:

        count = Counter()
        for product_element in self.product.elements:
            count[(product_element.elem_type, product_element.pack_id)] += 1
        return (
            count[(element.elem_type, element.pack_id)],
            element.name,
            element.pack_id,
            element.elem_type,
            element.material,
        )


class MetalElementsNesting(BaseNesting):
    included_elements = ['r']
    filename = 'metal_elements.csv'

    def __init__(self, product, element):
        self.element = element
        super().__init__(product)

    def __call__(self, **kwargs) -> str:
        for filename, rows in self.filenames_with_rows.items():
            # only one so we can return it
            return self.get_file(rows)

    def _is_element_excluded(self, element: Element) -> bool:
        return element.elem_type not in self.included_elements

    def get_filename_for_element(self, element: Element) -> str:
        return f'metal_elements.csv'

    def get_row(
        self,
        element: Element,
    ) -> RowFlat:
        length = element.x2 - element.x1
        return (
            element.name,
            length,
        )

    def get_file(self, rows: list) -> str:
        output = io.StringIO()
        output.write('name;długość\n')
        for row in rows:
            output.write(f'{";".join(str(val) for val in row)}\n')
        return output.getvalue()
