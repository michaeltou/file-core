from multiprocessing import Pool, freeze_support
import engine.util.config as config
from engine.core.migrate_core_engine import *

# 批量处理进程池大小
BATCH_PROCESS_COUNT_FOR_TXT_WORKER = config.get_config_value("read_tool.file.batch.process.pool.size",4)


class TextWorker():
    def __init__(self ):
        # 使用全局进程池
        self.pool = self.gen_pool()

    @staticmethod
    def gen_pool(process_count=BATCH_PROCESS_COUNT_FOR_TXT_WORKER):
        local_pool = Pool(processes=BATCH_PROCESS_COUNT_FOR_TXT_WORKER)
        return local_pool

    def close_global_pool(self):
        """关闭全局进程池"""
        self.pool.close()  # 关闭进程池，不再接受新任务
        self.pool.join()  # 等待所有任务完成
        self.pool = None  # 将全局变量重置为None


    def read_txt_file_for_one_process(self, uuid, tuple_param_list):
        start_time_submit = time.time()
        log.info("uuid:%s, 开始提交任务到进程池", uuid)
        # 提交任务到进程池
        self.pool.starmap(one_process_do_task_for_text_file, tuple_param_list)
        log.info("uuid:%s, 提交任务到进程池，总耗时 %s 秒", uuid, time.time() - start_time_submit)
        self.close_global_pool()


def one_process_do_task_for_text_file(flow_node_txt_config,
                                         my_dataframe,
                                         filter_logic,
                                         target_interface_table,
                                         field_mapping_config_list,
                                          context_instance ):
    uuid = context_instance.get('[UUID]')
    log.info("uuid:%s, 进程:%s 开始处理任务,记录数：%s", uuid, os.getpid(), len(my_dataframe))
    # 创建读数引擎
    migrate_core_engine = MigrateCoreEngine()
    migrate_core_engine.dataframe_to_oracle(flow_node_txt_config,
                                            my_dataframe, filter_logic,
                                            target_interface_table,
                                            field_mapping_config_list,
                                            context_instance)

    return None