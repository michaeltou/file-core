from engine.split.record.FileSplitRecord import FileSplitRecord
from engine.split.record.FileExceptionLog import FileExceptionLog


def insert_split_record(uuid, md5_value, file_path_and_name_dto, file_split_rule, status, message, start_time, end_time):
    my_uuid = uuid
    rule_id = file_split_rule.get('ruleId')
    rule_name = file_split_rule.get('ruleName')
    file_path_and_name = file_path_and_name_dto.get('filePathAndName')

    my_message = message[:1900] + '...' if len(message) > 1900 else message

    file_split_record = FileSplitRecord(
        uuid=my_uuid, rule_id=rule_id,
        rule_name=rule_name, file_path_and_name=file_path_and_name,
        md5=md5_value, status=status, message=my_message,
        start_time=start_time, end_time=end_time
        )

    file_split_record.insert_record()


def insert_exception_log(uuid, file_path_and_name_dto, file_split_rule, exception_type, message):
    my_uuid = uuid
    rule_id = file_split_rule.get('ruleId')
    rule_name = file_split_rule.get('ruleName')
    file_path_and_name = file_path_and_name_dto.get('filePathAndName')

    my_message = message[:1900] + '...' if len(message) > 1900 else message

    file_exception_log = FileExceptionLog(
        uuid=my_uuid, rule_id=rule_id,
        rule_name=rule_name, file_path_and_name=file_path_and_name,exception_type=exception_type,
        message=my_message
        )

    file_exception_log.insert_record()


