import flet as ft

import sys 
import os 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from CustomComponentFactory import CustomComponentFactory, ColumnSpec, TableType

from faker import Faker 

def generate_random_data(num_elements): 
    fake = Faker() 
    data = [] 
    for _ in range(num_elements): 
        person = { 
            "name": fake.first_name(), 
            "surname": fake.last_name(), 
            "address": fake.street_address(), 
            "city": fake.city(), 
            "country": fake.country_code() 
        } 
        
        data.append(person) 
    
    return data

def main(page: ft.Page):

    columns = [
        ColumnSpec("NAME", 'name'),
        ColumnSpec("SURNAME", 'surname'),
        ColumnSpec("ADDRESS", 'address'),
        ColumnSpec("CITY", 'city'),
        ColumnSpec("COUNTRY", 'country')
    ]

    table = CustomComponentFactory.create_data_table(  
        TableType.PAGINATED,
        columns,
        generate_random_data(100)
    )

    page.add(
        ft.Text("Paginated data table", size=30),
        table
    )

ft.app(target=main)
