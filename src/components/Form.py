


import flet as ft
from typing import Any

class ValueSpec():
    def __init__(self, value, width=None, disabled: bool = False) -> None:
        self.value = value
        self.width = width
        self.disabled = disabled

class ItemSpec():

    def __init__(self, key: str, value: Any | ValueSpec, visible=True) -> None:
        self.key = key
        self.value = value
        self.visible = visible

class Form(ft.UserControl):
    def __init__(self, items: list[ItemSpec]) -> None:

        form_entries = ft.Column([])

        for item in items:
            if not isinstance(item.value, ValueSpec):
                form_entries.controls.append(
                    ft.Row(
                        controls=[
                            ft.Text(f"{item.key}:" if len(item.key) > 0 else f"{item.key}", weight=ft.FontWeight.BOLD, visible=item.visible), ft.Text(f"{item.value}")
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
            else:
                form_entries.controls.append(
                    ft.Row(
                        [
                            ft.TextField(label=item.key, value=item.value.value, disabled=item.value.disabled, visible=item.visible, width=item.value.width, border=ft.InputBorder.OUTLINE)
                        ] 
                        if item.value.width else
                        [
                            ft.TextField(label=item.key, value=item.value.value, disabled=item.value.disabled, visible=item.visible, width=200, border=ft.InputBorder.OUTLINE)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                )
        
        form_entries.controls.append(
            ft.Row(
                [
                    ft.Text('', visible=False, color=ft.colors.RED, size=12)
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )

        self.form_entries = form_entries
        self.items = items

        ft.UserControl.__init__(self)
    
    def get_value_by_key(self, key: str) -> ft.Control:
        for idx, item in enumerate(self.items):
            if item.key == key:
                return self.form_entries.controls[idx].controls[0].value
    
    def update_value_by_key(self, key: str, value: any):
        for idx, item in enumerate(self.items):
            if item.key == key and not isinstance(item.value, ValueSpec):
                self.form_entries.controls[idx].controls[1].value = value
                self.update()
    
    def get_control_index_by_key(self, key: str):
        for idx, item in enumerate(self.items):
            if item.key == key:
                return idx
    
    def display_error_message(self, msg: str):
        self.form_entries.controls[-1].controls[0].value = msg
        self.form_entries.controls[-1].controls[0].visible = True
        self.update()

    def build(self):
        return self.form_entries