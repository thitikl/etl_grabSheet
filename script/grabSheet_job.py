import datetime as dt
from typing import Optional
import pandas as pd
import numpy as np
import xlsxwriter
from .base_job import BaseJob
from logging import Logger

JOB_NAME = "grabSheet_job"
JOB_PURPOSE = "Rearrange customer data for grab sheet"
LOGGER_NAME = "grabSheet_job"
ADDITIONAL_CFG = {
    "order_path": "",
    "stop_path": "",
    "output_path": ""
}


class GrabSheetJOB(BaseJob):
    def __init__(self, cfg_path: str, cfg_section: str):
        super().__init__(
            is_logging=True,
            cfg_path=cfg_path,
            job_name=JOB_NAME,
            job_purpose=JOB_PURPOSE,
            logger_name=LOGGER_NAME,
            additional_default_cfg=ADDITIONAL_CFG,
            cfg_section=cfg_section
        )

    def perform_operations(self,
                           logger: Logger,
                           as_of_date: Optional[dt.date] = None,
                           as_of_hour: Optional[int] = None):
        logger.info("Getting paths from config file")
        order_path = self.cfg_map.get("order_path")
        stop_path = self.cfg_map.get("stop_path")
        output_path = self.cfg_map.get("output_path")

        logger.info("Reading input files")
        order_df = pd.read_excel(order_path, index_col="id")
        stop_df = pd.read_excel(stop_path)

        final_df = stop_df.merge(order_df, on="name")
        final_df.sort_values(["route", "stop"])
        routes = final_df["route"].sort_values().unique()
        writer = pd.ExcelWriter(output_path, engine="xlsxwriter")

        for route in routes:
            logger.info(f"Transforming data from route{route}")
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
            logger.info(f"Writing output file from route{route} on sheet route_{route}")
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

            header_fmt = workbook.add_format({'bold': 1})
            header_list = list(after_sum_df.columns)
            header_list[0] = route
            worksheet.write_row("A1", header_list, header_fmt)
            worksheet.autofit()
        writer.close()
        logger.info("Finish transforming data for grab sheet")
