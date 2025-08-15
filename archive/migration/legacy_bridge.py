"""Legacy Compatibility Bridge
Provides backward compatibility during Phase 2 migration
DEPRECATED: This module will be removed in Phase 3
"""
import warnings


def deprecated_warning(old_module: str, new_service: str):
    """Issue deprecation warning"""
    warnings.warn(
        f"{old_module} is deprecated. Use {new_service} instead.",
        DeprecationWarning,
        stacklevel=3
    )


class LegacyReportProcessor:
    """Deprecated: Use services / report - generator API instead"""

    def __init__(self, *args, **kwargs):
        deprecated_warning("ReportProcessor", "services / report - generator")
        # Minimal compatibility implementation
        pass

    def process_csvs(self, *args, **kwargs):
        deprecated_warning("process_csvs", "POST /process endpoint")
        raise NotImplementedError("Use report - generator service API")


class LegacyCSVTransformer:
    """Deprecated: Use services / report - generator / csv_processor instead"""

    def __init__(self, *args, **kwargs):
        deprecated_warning("CSVTransformer", "services / report - generator")
        pass

    def transform(self, *args, **kwargs):
        deprecated_warning("transform", "POST /transform endpoint")
        raise NotImplementedError("Use report - generator service API")


class LegacyExcelWriter:
    """Deprecated: Use services / report - generator / excel_generator instead"""

    def __init__(self, *args, **kwargs):
        deprecated_warning("ExcelWriter", "services / report - generator")
        pass

    def write_daily(self, *args, **kwargs):
        deprecated_warning("write_daily", "POST /process endpoint")
        raise NotImplementedError("Use report - generator service API")

# Compatibility imports (deprecated)
ReportProcessor = LegacyReportProcessor
CSVTransformer = LegacyCSVTransformer
ExcelWriter = LegacyExcelWriter