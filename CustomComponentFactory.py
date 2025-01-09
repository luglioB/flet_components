
from typing import TypeVar, List
from enum import Enum

from .components.PaginatedDatatable import PaginatedDataTable
from .components.LazyPaginatedDatatable import LazyPaginatedDataTable
from .components.BasicDataTable import BasicDataTable
from .components._DataTable import ColumnSpec
from .components.Form import ItemSpec, Form

T = TypeVar('T')

class TableType(Enum): 
    PAGINATED = "Paginated" 
    LAZY_PAGINATED = "LazyPaginated" 
    BASIC = "Basic"

class CustomComponentFactory():

    @staticmethod
    def create_data_table(
            type: TableType,
            columns: list[ColumnSpec],
            data: List[T],
            on_select_changed_callback = None,
            lazy_callback=None,
            rows_per_page=10,
            count=None):

        """ Create a data table of the specified type. 
        
            Args: 
                type (TableType): The type of the data table. 
                columns (List[ColumnSpec]): The columns specifications. 
                data (List[T]): The data to be displayed. 
                on_select_changed_callback (Callable, optional): Callback for selection change. 
                lazy_callback (Callable, optional): Callback for lazy loading. 
                rows_per_page (int, optional): Number of rows per page. Defaults to 10. 
                count (int, optional): Total number of items. Defaults to None. 
                
            Returns: 
                Union[PaginatedDataTable, LazyPaginatedDataTable, BasicDataTable]: An instance of the requested data table type. """

        common_args = { 
            'columns': columns, 
            'data': data, 
            'on_select_changed_callback': on_select_changed_callback
        }

        if type == TableType.PAGINATED:
            return PaginatedDataTable(
                **common_args,
                rows_per_page=rows_per_page
            )

        elif type == TableType.LAZY_PAGINATED:
            return LazyPaginatedDataTable(
                **common_args,
                lazy_callback=lazy_callback,
                rows_per_page=rows_per_page,
                count=count
            )

        elif type == TableType.BASIC:
            return BasicDataTable(
                **common_args
            )
        else:
            raise ValueError(f"Unknown table type: {type}")

    @staticmethod
    def create_form(items: list[ItemSpec]):
        return Form(items)