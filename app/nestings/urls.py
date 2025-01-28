from django.urls import path

from nestings.views import NestingFilesView

urlpatterns = [
    path(
        'nestings/',
        NestingFilesView.as_view(),
        name='nestings_nesting_files-list',
    ),
]