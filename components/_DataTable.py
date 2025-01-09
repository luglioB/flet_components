

import flet as ft
import pyperclip as pc
from uuid import uuid4
from dataclasses import dataclass
from typing import Optional, TypeVar, Generic, List
from threading import Thread
import queue
from datetime import datetime

from ..utils.PauseableThread import PauseableThread

T = TypeVar('T')

@dataclass
class CustomAction():
    display_name: str
    callback: any
    icon: str = None
    disabled_callback: any = None
    visible_callback: any = None
    color: Optional[str] = ft.colors.BLUE

class ColumnSpec():

    def __init__(self, name: str, original_field_name: str = '', visible=True, custom_actions: list[CustomAction] = None) -> None:
        self.name = name
        self.original_field_name = original_field_name
        self.visible = visible
        self.custom_actions = custom_actions

class ToggleFilterSpec():
    def __init__(self, name: str, callback) -> None:
        self.name = name
        self.callback = callback

class _DataTable(Generic[T]):

    dataset: List[T] = []
    formatted_columns = []

    def __init__(self, columns: list[ColumnSpec],
            data: list[T],
            on_select_changed_callback = None) -> None:
        
        self.formatted_columns = []
        
        self.dataset = data

        self.table_uuid = str(uuid4())
        
        datacolumns = self.generate_datacolumns(columns)
        
        datarows = self.generate_datarows(columns, self.dataset, on_select_changed_callback)
        
        self.datatable = self.generate_datatable(datacolumns, datarows)

        self.num_rows = len(self.datatable.rows)

        self.on_select_changed_callback = on_select_changed_callback
        self.column_spec = columns
        self.expiration_watcher_started = False
        self.expiration_watcher_column_to_check = None
        self.expiration_watcher_column_to_update = None

        self.q = queue.Queue()
        Thread(target=self.background_worker, daemon=True).start()

    def background_worker(self):
        print(f"starting background worker for table {self.table_uuid}")
        while True:
            item = self.q.get()
            item.start()
            item.join()
            self.q.task_done()
    
    def generate_datatable(self, columns: list[ft.DataColumn], rows: list[ft.DataRow]):
        return ft.DataTable(
            columns=columns,
            rows=rows,
            sort_column_index=0,
            sort_ascending=False,
            data_text_style=ft.TextStyle(size=11),
            data_row_min_height=38,
            data_row_max_height=40,
            column_spacing=0.5,
            horizontal_lines=ft.border.BorderSide(0.1, ft.colors.GREY),
            show_bottom_border=True,
            heading_text_style=ft.TextStyle(size=12, weight=ft.FontWeight.BOLD),
            bgcolor="#2d2d2d",
            heading_row_color=ft.colors.BLACK26,
            border_radius=5,
            heading_row_height=50,
            expand=True
        )

    def generate_datacolumns(self, columns: list[ColumnSpec]) -> list[ft.DataColumn]:
        _columns = [ft.DataColumn(ft.Text(c.name), visible=c.visible) for c in columns]
        _columns.append(ft.DataColumn(ft.Text("row_uuid"), visible=False))
        return _columns
    
    def generate_datarows(self, columns: list[ColumnSpec], data: list[any], on_select_changed_callback = None) -> list[ft.DataRow]:
        
        def unpack_obj(obj):
            if not hasattr(obj, '__dict__'):
                return obj
            result = {}
            for key, val in vars(obj).items():
                if hasattr(val, '__dict__'):
                    result[key] = unpack_obj(val)
                else:
                    result[key] = val
            return result
        
        datarows = []

        for idx, d in enumerate(data):
            # obj = d.__dict__
            obj = unpack_obj(d)

            row_id = str(uuid4()) # unique row identifier

            datacells = []
            for c in columns:
                if c.custom_actions:
                    # all actions belonging to the same ColumnSpec will use the same callback; there is probably an error in this loop

                    buttons = [
                        ft.OutlinedButton(
                            action.display_name, 
                            on_click=lambda e: action.callback(e), 
                            data=row_id, 
                            disabled=action.disabled_callback(obj) if action.disabled_callback else False,
                            visible=action.visible_callback(obj) if action.visible_callback else True,
                            style=ft.ButtonStyle(color=action.color),
                            scale=0.7
                        )
                        if not action.icon
                        else ft.IconButton(
                            icon=action.icon, 
                            icon_color=action.color, 
                            on_click=lambda e: action.callback(e), 
                            data=row_id, 
                            disabled=action.disabled_callback(obj) if action.disabled_callback else False,
                            visible=action.visible_callback(obj) if action.visible_callback else True,
                            scale=0.7
                        )

                        for action in c.custom_actions 
                    ]
                    datacells.append(ft.DataCell(ft.Row(controls=buttons, spacing=0), visible=c.visible))     
                else:
                    if c.original_field_name != '':
                        try:
                            if "." in c.original_field_name:
                                _field = c.original_field_name.split(".")
                                target = obj[_field[0]][_field[1]]
                            else:
                                target = obj[c.original_field_name]
                            datacells.append(ft.DataCell(ft.Text(target, visible=c.visible), visible=c.visible))
                        except Exception as e:
                            datacells.append(ft.DataCell(ft.Text('', visible=c.visible), visible=c.visible))
                    else:     
                        datacells.append(ft.DataCell(ft.Text('', visible=c.visible), visible=c.visible))

            datacells.append(ft.DataCell(ft.Text(row_id), visible=False))

            datarow = ft.DataRow(
                    cells=datacells,
                    selected=False,
                    on_long_press=self.copy_to_clipboard,
                )

            if on_select_changed_callback:
                datarow.on_select_changed = lambda e: on_select_changed_callback(e)

            datarows.append(datarow)
        
        return datarows

    def get_row_by_uuid(self, uuid: str) -> ft.DataRow:
        for row in self.datatable.rows:
            if row.cells[-1].content.value == uuid:
                return row
            
    def remove_row_by_uuid(self, uuid: str):
        row = self.get_row_by_uuid(uuid)
        self.remove_row(row)

    def get_rows(self) -> list[ft.DataRow]:
        return self.datatable.rows
    
    def get_dataset(self) -> List[T]:
        return self.dataset

    def copy_to_clipboard(self, event: ft.ControlEvent):
        row: ft.DataRow = event.control
        pc.copy(row.cells[0].content.value)

    def update_row_expiration(self, column_to_check: str, column_to_update: str, callback: any = None):
        
        self.expiration_watcher_column_to_check = column_to_check
        self.expiration_watcher_column_to_update = column_to_update

        self.expiration_update_thread = PauseableThread(
            f"row_exp_{column_to_update}",
            self.watch_expiration, 
            self.expiration_watcher_column_to_check, 
            self.expiration_watcher_column_to_update,
            callback
        )
        
        self.expiration_update_thread.start()
    
    def build(self):
        pass
    
    def redraw(self, dataset: list[T], highlighted_row_number = None, count=None):
        pass

    def format_column(self, column_name_to_format: str, _format: str, column_name_values: any=None, callback: any=None):
        """Applies given format to entire column.
        
        column_name_to_format: the column to format
        _format: mnemonic name for format - COMMAS, FIX_DATE, FIX_DATETIME
        column_name_values: the column to take values from. It can be equal to column_name_to_format itself if you wish to use the same values
        callback: function that will apply the given format to each value according to a custom logic. The callback must accept a Datarow
        """
        # mantain a reference of the formatted columns so that on successive redraws the same formatting is applied automatically
        for row in self.datatable.rows:
            column_to_format_idx = 0
            column_value = 0
            idx = 0
            while idx < len(self.column_spec):
                if self.column_spec[idx].name == column_name_to_format:
                    column_to_format_idx = idx
                    break
                idx += 1
            
            if column_name_values:
                idx = 0
                while idx < len(self.column_spec):
                    if self.column_spec[idx].name == column_name_values:
                        column_value = idx
                        break
                    idx += 1

            try:
                if callback:
                    # row.cells[column_to_format_idx].content.value = callback(row)
                    row.cells[column_to_format_idx] = callback(row)
                elif _format == "COMMAS":
                    row.cells[column_to_format_idx].content.value = ("{:,}".format(int(row.cells[column_value].content.value)))
                elif _format == "FIX_DATE":
                    # converts from YYYYMMDD to YYYY-MM-DD
                    
                    original_date = str(row.cells[column_value].content.value)
                    year = original_date[:4]
                    month = original_date[4:6]
                    day = original_date[6:]
                    row.cells[column_to_format_idx].content.value = f"{year}-{month}-{day}"
                elif _format == "FIX_DATETIME":
                    # converts from YYYYMMDD-HH:MM:SS to datetime
                    
                    original_date = str(row.cells[column_value].content.value)
                    row.cells[column_to_format_idx].content.value = datetime.strptime(original_date, '%Y%m%d-%H:%M:%S')
            except Exception as e:
                print(e)
        
        if not self.formatted_columns or not any(d['column_name_to_format'] == column_name_to_format for d in self.formatted_columns):
            self.formatted_columns.append({
                'column_name_to_format': column_name_to_format,
                '_format': _format,
                'callback': callback,
                'column_name_values': column_name_values
            })

    def format_row(self, row_number, color, column_name=None):
        """Apply a custom format to a given row"""
        row_format_thread = Thread(
            target=self._execute_row_format, args=(row_number, color, column_name,), daemon=True
        )
        self.q.put(row_format_thread)
        self.q.join()

    def highlight_row(self, row_number):
        """Highlights a given row for a short amount of time"""
        row_highlight_thread = Thread(
            target=self._execute_row_highlight, args=(row_number,), daemon=True
        )
        self.q.put(row_highlight_thread)
        self.q.join()

    def _execute_row_highlight(self, row_number):
        pass

    def _execute_row_format(self, row_number, color, column_name=None):
        pass

    def remove_row(self, row: ft.DataRow):
        pass

    def watch_expiration(self, column_to_check: str, column_to_update: str, callback: any = None):
        """A function to update the expiration time of all rows, once the expiration time is reached, the row is removed.

        column_to_check: column containing datetime values
        column_to_update: column containing integer values that must be updated
        callback: function that will be called on expiration. It must accept a DataRow as argument
        """
        pass