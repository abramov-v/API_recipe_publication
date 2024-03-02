from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Paginator for the limit parameter."""

    page_size_query_param = 'limit'
    page_size = 6
