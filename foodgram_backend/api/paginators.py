from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    """Пагинатор для ожидается параметра limit."""
    page_size_query_param = 'limit'
