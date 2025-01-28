import io
import zipfile

from typing import Iterator, Iterable

from nestings.services.wondreful.nesting import WondrefulNewNesting, WondrefulNesting, MetalElementsNesting

FileWithName = tuple[str, bytes]

SHELF_TYPES_SHORTCUTS = {
    0: 'T1',
    1: 'T2',
}


class WondrefulNestingFilesGetter:

    def __init__(self, product) -> None:
        self.product = product
        self.nesting_files_generators = (
            WondrefulNesting(product),
        )
        if self.add_plywood_file:
            self.nesting_files_generators += (WondrefulNewNesting(product),)
        self.metal_elements = ('Rd', )
        if product.shelf_type == 0:
            self.metal_elements = ('R', 'M', 'Te')
        self.generate_base_nestings = True
        self.generate_metal_nestings = True

    def __call__(
        self,
        generate_base_nestings: bool = True,
        generate_metal_nestings: bool = True,
        **kwargs,
    ) -> io.BytesIO:
        self.generate_base_nestings = generate_base_nestings
        self.generate_metal_nestings = generate_metal_nestings
        return io.BytesIO(self._get_zip_with_files(self._nesting_files()))

    def get_filename_for_zip_with_grouped_files(self) -> str:
        """Returns filename for zip with drawer plywood components."""
        shelf_type_shortcut = SHELF_TYPES_SHORTCUTS[self.product.shelf_type]
        return f'{shelf_type_shortcut}_B{self.product.id}_S12.zip'

    @property
    def add_plywood_file(self) -> bool:
        has_type_02_plywood_drawer = (
            self.product.version < 8
            and self.product.shelf_type == 1
        )
        has_type_01_plywood_drawer = (
            self.product.version < 11
            and self.product.shelf_type == 0
        )
        return has_type_01_plywood_drawer or has_type_02_plywood_drawer

    def _get_zip_with_files(self, files: Iterable[FileWithName]) -> bytes:
        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zip_obj:
            for filename, file_content in files:
                zip_obj.writestr(filename, file_content)
        return zip_output.getvalue()

    def _nesting_files(self) -> Iterator[FileWithName]:
        if self.generate_base_nestings:
            for generator in self.nesting_files_generators:
                yield generator()
        if self.generate_metal_nestings and self.are_metal_nestings_needed:
            yield from self._metal_nesting_files_with_names()

    def _metal_nesting_files_with_names(self) -> Iterator[FileWithName]:
        for element in self.metal_elements:
            nesting_generator = MetalElementsNesting(self.product, element)
            filename = nesting_generator.filename
            yield filename, nesting_generator()

    @property
    def are_metal_nestings_needed(self) -> bool:
        return self.product.has_metal_elements
