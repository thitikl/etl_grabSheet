import pandas as pd
import numpy as np
import os
import xlsxwriter

order_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'input', 'customer_order.xlsx'))
stop_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'input', 'customer_stop.xlsx'))
output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output', 'output.xlsx'))

order_df = pd.read_excel(order_path, index_col="id")
stop_df = pd.read_excel(stop_path)

final_df = stop_df.merge(order_df, on="name")

final_df.sort_values(["route", "stop"])

routes = final_df["route"].sort_values().unique()

writer = pd.ExcelWriter(output_path, engine="xlsxwriter")

for route in routes:
    designated_df = final_df[final_df["route"] == route].reset_index(drop=True)
    sum_df = designated_df.groupby(designated_df.index // 6).sum()
    sum_df["name"] = "Grab#"
    sum_df[["route", "stop"]] = np.nan
    sum_df.index = (sum_df.index + 1) * 6 - 0.5
    after_sum_df = pd.concat([designated_df, sum_df], sort=False).sort_index()
    after_sum_df = after_sum_df.drop(columns=["route"])
    after_sum_df = after_sum_df[["stop"] + [col for col in after_sum_df.columns if col not in ["stop"]]]
    after_sum_df.to_excel(writer, sheet_name=f"route_{route}", index=False)

    workbook = writer.book
    worksheet = writer.sheets[f"route_{route}"]
    grab_fmt = workbook.add_format({
        'bg_color': '#EBF1DE',
        'bold': 1})
    worksheet.conditional_format('A1:H10000',
                                 {'type': 'formula',
                                  'criteria': '=$B1="Grab#"',
                                  'format': grab_fmt
                                  })

    border_fmt = workbook.add_format({'bottom': 1, 'top': 1, 'left': 1, 'right': 1})
    worksheet.conditional_format(xlsxwriter.utility.xl_range(0, 0, len(after_sum_df), len(after_sum_df.columns) - 1),
                                 {'type': 'no_errors', 'format': border_fmt})

    header_fmt = workbook.add_format({'font_size': 16, 'bold': 1})
    header_list = list(after_sum_df.columns)
    header_list[0] = route
    worksheet.write_row("A1", header_list, header_fmt)
    worksheet.autofit()
writer.close()
