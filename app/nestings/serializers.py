import dataclasses

from rest_framework import serializers


@dataclasses.dataclass
class Element:
    name : str
    x1 : int
    x2 : int
    y1 : int
    y2 : int
    z1 : int
    z2 : int
    pack_id : int
    elem_type : str
    material : int

    @property
    def type(self):
        return {
            'h': 'horizontal',
            'v': 'vertical',
            's': 'support',
            'd': 'door',
            't': 'drawer',
            'r': 'rail',
        }


@dataclasses.dataclass
class Shelf:
    id : int
    elements : list[dict[str, str | int]]
    producer : str
    shelf_type : int
    version : int

    @property
    def has_metal_elements(self):
        return any(element.elem_type == 'r' for element in self.elements)


class ElementSerializer(serializers.Serializer):
    name = serializers.CharField()
    x1 = serializers.IntegerField()
    x2 = serializers.IntegerField()
    y1 = serializers.IntegerField()
    y2 = serializers.IntegerField()
    z1 = serializers.IntegerField()
    z2 = serializers.IntegerField()
    pack_id = serializers.IntegerField()
    elem_type = serializers.CharField()
    material = serializers.IntegerField()

    def to_internal_value(self, data):
        return Element(**data)


class ShelfSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    elements = ElementSerializer(many=True)
    producer = serializers.CharField()
    shelf_type = serializers.IntegerField()
    version = serializers.IntegerField()

    def to_internal_value(self, data):
        elements = data.pop('elements')
        data['elements'] = [Element(**element) for element in elements]
        return Shelf(**data)
