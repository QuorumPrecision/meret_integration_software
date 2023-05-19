
REM "Before building run: python -m pip install -U pyinstaller"

start cmd /k "pyinstaller --onefile bap2_logger.py && move dist\bap2_logger.exe ."