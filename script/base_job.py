import logging
from logging.handlers import TimedRotatingFileHandler
from configparser import ConfigParser
import os
import pathlib
from typing import Optional, Dict, Any
import datetime as dt

CFG_DATEFMT = '%Y-%m-%d'


class BaseJob:
    def __init__(self, is_logging: bool,
                 cfg_path: str,
                 job_name: str,
                 job_purpose: str,
                 logger_name: str,
                 additional_default_cfg: Optional[Dict[str, Any]] = None,
                 cfg_section: Optional[str] = None):

        # Set job specific details
        self.job_name = job_name
        self.job_purpose = job_purpose

        # Config file configuration
        self.cfg_map = dict()
        config = ConfigParser()
        config.read(cfg_path)
        if not config:
            raise ValueError(f"'{cfg_path}' configuration file cannot be read.")
        active_cfg_section = "DEFAULT"

        if cfg_section and config.has_section(cfg_section):
            active_cfg_section = cfg_section

        active_cfg = config[active_cfg_section]
        # Get common config value
        self.cfg_map['log_dir_path'] = active_cfg.get('log_dir_path')
        self.cfg_map['log_max_files'] = int(active_cfg.get('log_max_files', '7'))
        self.cfg_map['log_file_name'] = active_cfg.get('log_file_name')

        # Logger configuration
        if is_logging:
            log_sub_dir_path = self.cfg_map['log_file_name']
            log_path = os.path.join(self.cfg_map['log_dir_path'], log_sub_dir_path)
            pathlib.Path(log_path).mkdir(parents=True, exist_ok=True)
            filename = os.path.join(log_path, f"{self.cfg_map['log_file_name']}.log")
            log_handlers = [TimedRotatingFileHandler(
                filename=filename, when='midnight', backupCount=self.cfg_map['log_max_files']
            ), logging.StreamHandler()]
        else:
            log_handlers = [logging.StreamHandler()]

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s.%(msecs)03d [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] %('
                                   'funcName)s() - ' \
                                   '%(message)s',
                            handlers=log_handlers)
        self.logger = logging.getLogger(name=logger_name)

        # Additional config values
        if additional_default_cfg is None:
            additional_default_cfg = dict()
        for key in additional_default_cfg:
            self.cfg_map[key] = active_cfg.get(key, additional_default_cfg[key])

    def perform_operations(self, logger: logging.Logger,
                           as_of_date: Optional[dt.date] = None,
                           as_of_hour: Optional[int] = None):
        pass

    def run(self, as_of_date: Optional[dt.date] = None, as_of_hour: Optional[int] = None):

        ##########################
        # Perform job operations #
        ##########################

        pass_text = f"Start {self.job_name} operations for {self.job_purpose} "
        if as_of_date:
            pass_text += f"as of {as_of_date.strftime(CFG_DATEFMT)} "
            if as_of_hour:
                pass_text += f"@ hour={as_of_hour} "
        self.logger.info(pass_text)

        # if self._gchat_webhook_info_url:
        #     pass_title = f'Start job [{self._job_name}]...'
        #     pass_subtitle = None
        #     if as_of_date:
        #         pass_subtitle = f"As of {as_of_date.strftime('%Y-%m-%d')}"
        #         if as_of_hour:
        #             pass_subtitle += f'@ hour={as_of_hour}'
        #     # Send info webhook to Google Chat
        #     self.send_gchat_msg_info(
        #         title=pass_title,
        #         subtitle=pass_subtitle,
        #         text=pass_text,
        #     )

        try:
            self.perform_operations(self.logger, as_of_date, as_of_hour)
        except Exception:
            alert_text = f"Exception is thrown while performing the {self.job_name} operations " \
                         f"for {self.job_purpose} "
            if as_of_date:
                alert_text += f"as of {as_of_date.strftime(CFG_DATEFMT)} "
                if as_of_hour:
                    alert_text += f"@ hour={as_of_hour} "
            alert_text += '.'
            self.logger.exception(alert_text)

            # if self._gchat_webhook_alert_url:
            #     alert_title = f"Exception from job [{self._job_name}]."
            #     alert_subtitle = None
            #     if as_of_date:
            #         alert_subtitle = f'As of {as_of_date.strftime(CFG_DATEFMT)}'
            #         if as_of_hour:
            #             alert_subtitle += f'@ hour={as_of_hour}'
            #
            #     alert_text = f"{alert_text}\n\n{str(traceback.format_exc())}"
            #     self.send_gchat_msg_alert(
            #         title=alert_title,
            #         subtitle=alert_subtitle,
            #         text=alert_text,
            #     )
            raise

        pass_text = f"Finish {self.job_name} operations for {self.job_purpose} "
        if as_of_date:
            pass_text += f"as of {as_of_date.strftime(CFG_DATEFMT)} "
            if as_of_hour:
                pass_text += f"@ hour={as_of_hour} "
        self.logger.info(pass_text)

        # if self._gchat_webhook_info_url:
        #     pass_title = f'Finish job [{self._job_name}].'
        #     pass_subtitle = None
        #     if as_of_date:
        #         pass_subtitle = f'As of {as_of_date.strftime(CFG_DATEFMT)}'
        #         if as_of_hour:
        #             pass_subtitle += f'@ hour={as_of_hour}'
        #     # Send info webhook to Google Chat
        #     self.send_gchat_msg_info(
        #         title=pass_title,
        #         subtitle=pass_subtitle,
        #         text=pass_text,
        #     )
