import flet as ft

def main(page: ft.Page):

    x = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    y = [1.2, 1.6, 9.6, 0.2, 1.3, 2.3, 3.5, 1.6, 1.02]

    chart_data = []

    i = 0
    for i in range(len(x)):
        chart_data.append(ft.LineChartDataPoint(x[i], y[i]))
    
    data = [
        ft.LineChartData(chart_data)
    ]

    line_chart = ft.LineChart(data, width=200)

    columns = [
        ft.DataColumn(ft.Text("Name")),
        ft.DataColumn(ft.Text("Line Chart"))
    ]

    rows = [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Row 1")),
                ft.DataCell(line_chart)  # Embed the chart in the table cell
            ]
        ),
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Row 2")),
                ft.DataCell(line_chart)  # Embed the same chart in another row for example
            ]
        )
    ]

    data_table = ft.DataTable(columns=columns, rows=rows)

    page.add(data_table)

ft.app(target=main)
