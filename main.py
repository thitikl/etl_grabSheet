from script import GrabSheetJOB
import argparse
import os
import datetime as dt

CFG_PATH = r"C:\Users\thiti\Projects(Coding)\Personal project\yumba_grabSheet\config\config.ini"


def main():
    # parser = argparse.ArgumentParser(prog="grabSheet")
    # parser.add_argument("--cfg_path")
    # cfg_path = vars(parser.parse_args())
    # print(cfg_path)
    # if not os.path.isfile(cfg_path):
    #     parser.error(f"'{cfg_path}' configuration file is not found.")
    job = GrabSheetJOB(CFG_PATH, cfg_section="GRAB_SHEET")
    job.run(as_of_date=dt.date.today(), as_of_hour=dt.datetime.now().time().hour)


main()
