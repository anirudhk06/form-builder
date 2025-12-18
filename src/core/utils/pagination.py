import math
from rest_framework.pagination import PageNumberPagination


class CustomLimitPagination(PageNumberPagination):
    page_size = 10
    def get_page_size(self, request):
        return request.query_params.get("page_size", self.page_size)
    def get_pagination_details(self) -> dict:
        return {
            "next": self.page.next_page_number() if self.page.has_next() else None,
            "previous": (
                self.page.previous_page_number() if self.page.has_previous() else None
            ),
            "current": self.page.number,
            "total_page": self.page.paginator.num_pages,
            "count": self.page.paginator.count,
        }




class MongoPageNumberPagination:
    page_size = 10
    page_query_param = "page"
    page_size_query_param = "page_size"
    max_page_size = 100

    def __init__(self, request):
        self.request = request
        self.page = self.get_page()
        self.page_size = self.get_page_size()
        self.skip = (self.page - 1) * self.page_size

    def get_page(self) -> int:
        try:
            page = int(self.request.query_params.get(self.page_query_param, 1))
        except:
            page = 1
        return max(page, 1)

    def get_page_size(self) -> int:
        try:
            size = int(
                self.request.query_params.get(
                    self.page_size_query_param, self.page_size
                )
            )
        except:
            size = self.page_size

        return min(size, self.max_page_size)

    def paginate(self, collection, query=None, sort=None, projection=None):
        query = query or {}

        total_count = collection.count_documents(query)
        total_page = math.ceil(total_count / self.page_size) if total_count else 1

        cursor = collection.find(query, projection)

        if sort:
            cursor = cursor.sort(*sort)

        cursor = cursor.skip(self.skip).limit(self.page_size)
        results = list(cursor)

        return results, total_count, total_page

    def get_paginated_response(self, results, total_count, total_page) -> dict:
        return {
            "next": self.page + 1 if self.page < total_page else None,
            "previous": self.page - 1 if self.page > 1 else None,
            "current": self.page,
            "total_page": total_page,
            "count": total_count,
            "results": results,
        }
