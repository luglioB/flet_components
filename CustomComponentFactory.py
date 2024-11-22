
from typing import TypeVar, List

from components.PaginatedDatatable import PaginatedDataTable
from components.LazyPaginatedDatatable import LazyPaginatedDataTable
from components.BasicDataTable import BasicDataTable
from components._DataTable import ColumnSpec
from components.Form import ItemSpec, Form

T = TypeVar('T')

class CustomComponentFactory():

    @staticmethod
    def create_data_table(
            type: str,
            columns: list[ColumnSpec],
            data: List[T],
            on_select_changed_callback = None,
            lazy_callback=None,
            rows_per_page=10,
            count=None):
        
        if type == 'Paginated':
            return PaginatedDataTable(
                columns,
                data,
                on_select_changed_callback,
                rows_per_page=rows_per_page
            )

        elif type == 'LazyPaginated':
            return LazyPaginatedDataTable(
                columns,
                data,
                on_select_changed_callback,
                lazy_callback=lazy_callback,
                rows_per_page=rows_per_page,
                count=count
            )

        elif type == 'Basic':
            return BasicDataTable(
                columns,
                data,
                on_select_changed_callback,
            )

    @staticmethod
    def create_form(items: list[ItemSpec]):
        return Form(items)