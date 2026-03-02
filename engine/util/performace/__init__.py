
from engine.util.performace.PerformanceMonitorLog import PerformanceMonitorLog
import engine.util.ip as ip


def insert_performance_log(context_instance, phase, status, message, start_time, end_time):
    my_uuid = context_instance.get('[UUID]')
    my_fund_id = context_instance.get('[FUND_ID]')
    my_business_date = context_instance.get('[BUSINESS_DATE]')
    my_interface_id = context_instance.get('[INTERFACE_ID]')
    my_interface_name = context_instance.get('[INTERFACE_NAME]')
    my_file_path_and_name = context_instance.get('[FILE_PATH_AND_NAME]')
    my_read_mode = context_instance.get('[READ_MODE]')
    my_ip_address = ip.get_ip()

    my_message = message[:1900] + '...' if len(message) > 1900 else message
    performance_monitor_log = PerformanceMonitorLog(
        uuid=my_uuid,
        fund_id=my_fund_id,
        business_date=my_business_date,
        interface_id=my_interface_id,
        interface_name=my_interface_name,
        file_path_and_name=my_file_path_and_name,
        read_mode=my_read_mode,
        phase=phase, status=status, message=my_message, ip_address=my_ip_address, start_time=start_time, end_time=end_time)

    performance_monitor_log.insert_log()

