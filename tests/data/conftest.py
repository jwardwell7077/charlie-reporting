# Directory structure for pytest-based unit tests
# 
# daily_report_automation/
# ├── src/
# ├── config/
# └── tests/
#     ├── data/                        # sample CSVs and YAMLs for test fixtures
#     │   ├── example_IB_Calls__2025-07-11.csv
#     │   └── columns_config.yaml       # copy or minimal stub from config/
#     ├── conftest.py                  # pytest fixtures
#     ├── test_utils.py                # tests for utils.py
#     ├── test_config_loader.py        # tests for config_loader.py
#     ├── test_email_fetcher.py        # tests for email_fetcher.py (mocked Outlook)
#     ├── test_transformer.py          # tests for transformer.py
#     ├── test_excel_writer.py         # tests for excel_writer.py
#     └── test_archiver.py             # tests for archiver.py

# Example conftest.py
doctest_content = '''
import os
import pytest
from config_loader import ConfigLoader

@ pytest.fixture(scope='session')
def config_loader(tmp_path_factory):
    # Copy a sample YAML into a temp directory
    sample = tmp_path_factory.mktemp('data') / 'columns_config.yaml'
    src = os.path.join(os.getcwd(), 'tests', 'data', 'columns_config.yaml')
    with open(src) as f_src, open(sample, 'w') as f_dst:
        f_dst.write(f_src.read())
    return ConfigLoader(str(sample))

@ pytest.fixture

def utils():
    import utils
    return utils

@ pytest.fixture

def transformer(tmp_path, config_loader):
    import transformer
    raw = tmp_path / 'raw'
    archive = tmp_path / 'archive'
    raw.mkdir()
    archive.mkdir()
    return transformer.CSVTransformer(config_loader, raw_dir=str(raw), archive_dir=str(archive))
'''  
print(doctest_content)  # placeholder; code will be split into files
