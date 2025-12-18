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
        