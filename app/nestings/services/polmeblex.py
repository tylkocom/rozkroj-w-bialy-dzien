import io
import json
import csv
import zipfile
from collections import defaultdict
from io import StringIO

from nestings.serializers import Element, Shelf


def calculate_dimensions(elem: Element):
    return {
        'length': abs(elem.x2 - elem.x1),
        'width': abs(elem.y2 - elem.y1),
        'depth': abs(elem.z2 - elem.z1)
    }

def create_element_csvs(shelf: Shelf):
    elem_types = defaultdict(list)

    for i, elem in enumerate(shelf.elements, 1):
        dims = calculate_dimensions(elem)
        elem_types[elem.elem_type].append({
            'id': i,
            'length': dims['length'],
            'width': dims['width'],
            'depth': dims['depth'],
            'name': elem.name,
            'material': elem.material
        })

    zip_output = io.BytesIO()
    with zipfile.ZipFile(zip_output, 'w') as zf:
        for elem_type, elements in elem_types.items():
            if elements:
                output = StringIO()
                writer = csv.DictWriter(output, fieldnames=['id', 'length', 'width', 'depth', 'name', 'material'])
                writer.writeheader()
                writer.writerows(elements)
                zf.writestr(f'{elem_type}_elements.csv', output.getvalue())
    return zip_output.getvalue()
