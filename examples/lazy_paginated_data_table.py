import flet as ft

import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from CustomComponentFactory import CustomComponentFactory, ColumnSpec, TableType

def main(page: ft.Page):

    columns = [
        ColumnSpec("NAME", 'name'),
        ColumnSpec("SURNAME", 'surname'),
        ColumnSpec("ADDRESS", 'address'),
        ColumnSpec("CITY", 'city'),
        ColumnSpec("COUNTRY", 'country')
    ]

    data = [
        {
            "name": "Frank",
            "surname": "Sinatra",
            "address": "770 Las Vegas Blvd",
            "city": "Las Vegas",
            "country": "US"
        },
        {
            "name": "Pino",
            "surname": "Mango",
            "address": "Via 28 Ottobre",
            "city": "Lagonegro",
            "country": "IT"
        },
        {
            "name": "Paul",
            "surname": "Hewson",
            "address": "Strathmore Rd",
            "city": "Killney",
            "country": "IE"
        }
    ]

    table = CustomComponentFactory.create_data_table(  
        TableType.LAZY_PAGINATED,
        columns,
        data,
        rows_per_page=1,
        count=len(data)
    )

    page.add(
        ft.Text("Lazy paginated data table", size=30),
        table
    )

ft.app(target=main)
