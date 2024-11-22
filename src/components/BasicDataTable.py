

import flet as ft
from typing import TypeVar, List

from ._DataTable import _DataTable, ColumnSpec

T = TypeVar('T')

class BasicDataTable(_DataTable, ft.UserControl):
    def __init__(
            self,
            columns: list[ColumnSpec],
            data: list[T],
            on_select_changed_callback = None,
    ):
        _DataTable.__init__(self, columns, data, on_select_changed_callback)
        ft.UserControl.__init__(self)

    def build(self):
        return ft.Row(
                    controls=[
                            ft.Column(
                                [   
                                    ft.Row(
                                        controls=[self.datatable],
                                    )
                                ],
                                expand=True
                            )
                        ],
                    expand=True
        )

    def redraw(self, dataset: list[T], highlighted_row_number = None, count=None):

        if self.expiration_watcher_started:
            self.expiration_update_thread.pause()

        self.dataset = dataset
        self.datatable.rows = []

        self.datatable.rows = self.generate_datarows(self.column_spec, dataset, self.on_select_changed_callback)
        self.num_rows = len(self.datatable.rows)

        self.update()

        if self.expiration_watcher_started:
            self.expiration_update_thread.resume()

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