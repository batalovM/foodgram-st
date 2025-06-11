from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'  # Параметр запроса для указания размера страницы
    max_page_size = 100  # Максимальный размер страницы