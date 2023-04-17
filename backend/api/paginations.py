from rest_framework.pagination import PageNumberPagination


class LimitCustomPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6
