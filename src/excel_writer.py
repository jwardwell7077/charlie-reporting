import os
import pandas as pd
from logger import LoggerFactory


class ExcelWriter:
    """
    ExcelWriter takes transformed data and writes it to a single Excel workbook,
    with one sheet per report.
    """
    def __init__(self, output_dir: str = 'data/output', log_file: str = 'report.log'):
        self.output_dir = output_dir
        self.logger = LoggerFactory.get_logger('excel_writer', log_file)
        os.makedirs(self.output_dir, exist_ok=True)

    def write(self, report_data: dict, date_str: str):
        """
        Write the report_data to an Excel file named report_<date_str>.xlsx.

        report_data: { sheet_name: [DataFrame, ...] }
        """
        if not report_data:
            self.logger.warning('No data to write to Excel.')
            return

        output_path = os.path.join(self.output_dir, f'report_{date_str}.xlsx')
        self.logger.info(f'Writing Excel report to {output_path}')

        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for sheet_name, df_list in report_data.items():
                    combined_df = pd.concat(df_list, ignore_index=True)
                    combined_df.to_excel(writer, sheet_name=sheet_name, index=False)
            self.logger.info('Excel report generation complete.')
        except Exception as e:
            self.logger.error(f'Failed to write Excel report: {e}', exc_info=True)
