

import flet as ft
from typing import TypeVar, List
import inspect

from ._DataTable import _DataTable, ColumnSpec
import time

T = TypeVar('T')

class LazyPaginatedDataTable(_DataTable, ft.UserControl):

    DEFAULT_ROW_PER_PAGE = 5

    def __init__(
            self,
            columns: list[ColumnSpec],
            data: List[T],
            on_select_changed_callback = None,
            lazy_callback = None,
            rows_per_page: int = DEFAULT_ROW_PER_PAGE,
            count = None
    ):
        """
        A customized user control which returns a paginated data table. It offers the possibility to organize data
        into pages and also define the number of rows to be shown on each page.

        :parameter datatable: a DataTable object to be used
        :parameter rows_per_page: the number of rows to be shown per page
        """
        _DataTable.__init__(self, columns, data, on_select_changed_callback)

        # self.dt = datatable
        self.rows_per_page = rows_per_page

        # number of rows in the table
        # self.num_rows = len(datatable.rows)
        if count == None:
            raise Exception("count must be specified with LazyPaginatedDatatable")
        
        self.num_rows = count
        self.current_page = 1

        # Calculating the number of pages.
        p_int, p_add = divmod(self.num_rows, self.rows_per_page)
        self.num_pages = p_int + (1 if p_add else 0)

        # will display the current page number
        self.v_current_page = ft.Text(
            str(self.current_page),
            tooltip="Double click to set current page.",
            weight=ft.FontWeight.BOLD
        )

        # textfield to go to a particular page
        self.current_page_changer_field = ft.TextField(
            value=str(self.current_page),
            dense=True,
            filled=False,
            width=40,
            on_submit=lambda e: self.set_page(page=e.control.value),
            visible=False,
            keyboard_type=ft.KeyboardType.NUMBER,
            content_padding=2,
            text_align=ft.TextAlign.CENTER
        )

        # gesture detector to detect double taps of its contents
        self.gd = ft.GestureDetector(
            content=ft.Row(controls=[self.v_current_page, self.current_page_changer_field]),
            on_double_tap=self.on_double_tap_page_changer,
        )

        # textfield to change the number of rows_per_page
        self.v_num_of_row_changer_field = ft.TextField(
            value=str(self.rows_per_page),
            dense=True,
            filled=False,
            width=40,
            on_submit=lambda e: self.set_rows_per_page(e.control.value),
            keyboard_type=ft.KeyboardType.NUMBER,
            content_padding=2,
            text_align=ft.TextAlign.CENTER
        )

        # will display the number of rows in the table
        self.v_count = ft.Text(weight=ft.FontWeight.BOLD)

        self.pdt = ft.DataTable(
            columns=self.datatable.columns,
            rows=self.build_rows(),
            data_text_style=self.datatable.data_text_style,
            heading_text_style=self.datatable.heading_text_style,
            bgcolor=self.datatable.bgcolor,
            heading_row_color=self.datatable.heading_row_color,
            border_radius=self.datatable.border_radius,
            heading_row_height=self.datatable.heading_row_height,
            divider_thickness=self.datatable.divider_thickness,
            column_spacing=self.datatable.column_spacing,
            expand=self.datatable.expand,
            show_bottom_border=self.datatable.show_bottom_border,
            vertical_lines=self.datatable.vertical_lines,
            horizontal_lines=self.datatable.horizontal_lines,
            data_row_min_height=self.datatable.data_row_min_height,
            sort_ascending=self.datatable.sort_ascending
        )

        self.table_ft_column =  ft.Column(
            controls=[ft.Row([self.pdt])], scroll=ft.ScrollMode.AUTO
        )

        if lazy_callback:
            sig = inspect.signature(lazy_callback)
            if str(sig) != "(skip: int, limit: int)":
                raise ValueError("Function signature must be (skip: int, limit: int)")

        self.lazy_callback = lazy_callback
        self.skip = 0
        self.limit = self.rows_per_page

        ft.UserControl.__init__(self)

    def set_rows_per_page(self, new_row_per_page: str):
        pass

    def set_page(self, page: [str, int, None] = None, delta: int = 0):
        pass

    def next_page(self, e: ft.ControlEvent):
        """sets the current page to the next page"""
        if self.current_page < self.num_pages:
            
            skip = self.current_page  * self.rows_per_page
            res = self.lazy_callback(skip, self.rows_per_page)
            
            self.redraw_on_next_prev(res, self.current_page + 1)

    def prev_page(self, e: ft.ControlEvent):
        """set the current page to the previous page"""

        if (self.current_page - 1) > 0:
        
            if (self.current_page - 1) == 1:
                skip = 0
            # elif self.current_page == self.num_pages:
            #     num_rows = len(self.dataset)
            #     skip = (self.current_page - 1)  * (self.rows_per_page - num_rows)
            else:
                skip = (self.current_page - 2)  * self.rows_per_page

            res = self.lazy_callback(skip, self.rows_per_page)
            self.redraw_on_next_prev(res, self.current_page - 1)

    def build_rows(self) -> list:
        """
        Returns a slice of indexes, using the start and end values returned by the paginate() function
        :return: The rows of data that are being displayed on the page.
        """
        return self.datatable.rows[slice(*self.paginate())]

    def paginate(self) -> tuple[int, int]:
        """
        Returns a tuple of two integers, where the first is the index of the first row to be displayed
        on the current page, and `the second the index of the last row to be displayed on the current page
        :return: A tuple of two integers.
        """
        i1_multiplier = 0 if self.current_page == 1 else self.current_page - 1
        i1 = i1_multiplier * self.rows_per_page
        i2 = self.current_page * self.rows_per_page

        return i1, i2

    def get_height(self):
        while True:
            time.sleep(5)
            return 300
    
    def goto_first_page(self, e: ft.ControlEvent):
        if self.current_page > 1:
            res = self.lazy_callback(0, self.rows_per_page)
            self.redraw_on_next_prev(res, 1)

    def goto_last_page(self, e: ft.ControlEvent):
        if self.current_page < self.num_pages:
            skip = (self.num_pages - 1) * self.rows_per_page
            res = self.lazy_callback(skip, self.rows_per_page)
            self.redraw_on_next_prev(res, self.num_pages)

    def build(self): 
        return ft.Row(
            controls=[
                ft.Column(
                        [   
                            self.table_ft_column,
                            ft.Row(
                                [
                                    ft.Row(
                                        controls=[
                                            ft.IconButton(
                                                ft.icons.KEYBOARD_DOUBLE_ARROW_LEFT,
                                                on_click=self.goto_first_page,
                                                tooltip="First Page",
                                                icon_color=ft.colors.WHITE
                                            ),
                                            ft.IconButton(
                                                ft.icons.KEYBOARD_ARROW_LEFT,
                                                on_click=self.prev_page,
                                                tooltip="Previous Page",
                                                icon_color=ft.colors.WHITE
                                            ),
                                            self.gd,
                                            ft.IconButton(
                                                ft.icons.KEYBOARD_ARROW_RIGHT,
                                                on_click=self.next_page,
                                                tooltip="Next Page",
                                                icon_color=ft.colors.WHITE
                                            ),
                                            ft.IconButton(
                                                ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
                                                on_click=self.goto_last_page,
                                                tooltip="Last Page",
                                                icon_color=ft.colors.WHITE
                                            )
                                        ]
                                    ),
                                    self.v_count,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        expand=True
                    )
                ],
            expand=True
        )    

    def on_double_tap_page_changer(self, e):
        pass

    def refresh_data(self):
        self.pdt.rows = self.datatable.rows

        # display the total number of rows in the table.
        self.v_count.value = f"Total Rows: {self.num_rows}"
        # the current page number versus the total number of pages.
        self.v_current_page.value = f"{self.current_page}/{self.num_pages}"

        # update the visibility of controls in the gesture detector
        self.current_page_changer_field.visible = False
        self.v_current_page.visible = True

        if len(self.formatted_columns) > 0:
            for elem in self.formatted_columns:
                self.format_column(elem['column_name_to_format'], elem['_format'], elem['column_name_values'], elem['callback'])

        # update the control so the above changes are rendered in the UI
        self.update()

    def did_mount(self):
        self.refresh_data()

    def redraw(self, dataset: list[T], highlighted_row_number = None, count=None):
        
        if self.expiration_watcher_started:
            self.expiration_update_thread.pause()

        if count == None:
            raise Exception("count must be specified with LazyPaginatedDatatable")
        
        self.num_rows = count

        self.datatable.rows = []
        self.pdt.rows = []
        self.dataset = []

        self.dataset = dataset

        self.datatable.rows = self.generate_datarows(self.column_spec, dataset, self.on_select_changed_callback)

        self.current_page = 1

        p_int, p_add = divmod(self.num_rows, self.rows_per_page)
        self.num_pages = p_int + (1 if p_add else 0)

        self.refresh_data()

        if self.expiration_watcher_started:
            self.expiration_update_thread.resume()

    def redraw_on_next_prev(self, dataset: list[T], current_page):
        
        if self.expiration_watcher_started:
            self.expiration_update_thread.pause()

        self.datatable.rows = []
        self.pdt.rows = []
        self.dataset = []

        self.dataset = dataset

        self.datatable.rows = self.generate_datarows(self.column_spec, self.dataset, self.on_select_changed_callback)

        if self.current_page <= self.num_pages:
            self.current_page = current_page

        self.refresh_data()

        if self.expiration_watcher_started:
            self.expiration_update_thread.resume()

    def _execute_row_highlight(self, row_number):
        c = self.datatable.rows[row_number].color
        self.datatable.rows[row_number].color = "#a6a6a6"
        self.update()
        time.sleep(.14)
        self.datatable.rows[row_number].color = "#b3b3b3"
        self.update()
        time.sleep(.18)
        self.datatable.rows[row_number].color = "#bfbfbf"
        self.update()
        time.sleep(.08)
        self.datatable.rows[row_number].color = c
        self.update()

    def _execute_row_format(self, row_number, color, column_name=None):
        if not column_name:
            self.datatable.rows[row_number].color = ft.colors.with_opacity(0.3, color)
        else:
            cells = self.datatable.rows[row_number].cells
            idx = 0
            for cell in cells:
                 if self.column_spec[idx].name == column_name:
                    cell.color = color
                    self.datatable.rows[row_number].cells[idx] = cell

        self.update()
    
    def remove_row(self, row: ft.DataRow):
        for row_num, _row in enumerate(self.datatable.rows):
            if _row == row:
                self.datatable.rows.remove(row)
                self.dataset.pop(row_num)
                self.pdt.rows = []
                self.num_rows = len(self.datatable.rows)
                p_int, p_add = divmod(self.num_rows, self.rows_per_page)
                self.num_pages = p_int + (1 if p_add else 0)
                self.refresh_data()
                break
    
    def watch_expiration(self, column_to_check: str, column_to_update: str, callback: any = None):
        pass