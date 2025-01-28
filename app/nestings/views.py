from django.http import HttpResponse
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.views import APIView

from nestings.serializers import ShelfSerializer
from nestings.services.polmeblex import create_element_csvs
from nestings.services.wondreful.getters import WondrefulNestingFilesGetter


class NestingFilesView(APIView):
    """Api view to download nesting files."""

    def post(self, request: Request) -> HttpResponse:
        product = request.data.get('product')
        serializer = ShelfSerializer(data=product)
        serializer.is_valid(raise_exception=True)
        deserialized_product = serializer.validated_data
        if deserialized_product.producer == 'wondreful':
            nesting_data = WondrefulNestingFilesGetter(deserialized_product)()
        elif deserialized_product.producer == 'polmeblex':
            nesting_data = create_element_csvs(deserialized_product)
        elif deserialized_product.producer == 'BorderMebel':
            nesting_data = ''
        else:
            raise ValidationError('Incorrect producer!!!')
        response = HttpResponse(
            nesting_data,
            content_type='application/zip',
        )
        filename = f'{product["id"]}_nestings.zip'
        response['Content-Disposition'] = f'attachment; filename={filename}'
        response['Cache-Control'] = 'no-cache'
        return response