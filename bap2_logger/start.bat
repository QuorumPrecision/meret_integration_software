set "serial_port=COM10"
set "cadence=1"
set "modbus_id=1"

start cmd /k "bap2_logger.exe --port %serial_port% --cadence %cadence% --modbus_id %modbus_id%"