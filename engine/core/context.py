
class Context(object):
    def __init__(self):
        # 存储上下文变量
        self._context = {}
        # 存储简单上下文变量
        self._simple_context = {}

    def set(self, key, value):
        upper_key = key.upper()
        self._context[upper_key] = value
        simple_key = self.remove_brackets(upper_key)
        self._simple_context[simple_key] = value

    def get(self, key):
        upper_key = key.upper()
        return self._context.get(upper_key, None)

    def remove(self, key):
        upper_key = key.upper()
        if upper_key in self._context:
            del self._context[upper_key]
        if upper_key in self._simple_context:
            del self._simple_context[upper_key]

    def clear(self):
        self._context.clear()
        self._simple_context.clear()

    def __contains__(self, key):
        upper_key = key.upper()
        return upper_key in self._context

    def __len__(self):
        return len(self._context)

    def __iter__(self):
        return iter(self._context)

    def __str__(self):
        return f"context_instance content is: {self._context}"

    @staticmethod
    def remove_brackets(s):
        return s.strip('[]')

    def gen_simple_context_dict(self):
        """
        生成简单上下文字典，不包含[]的上下文
        :return:
        """
        return self._simple_context

    def gen_original_context_dict(self):
        """
        生成 上下文字典，包含[]的上下文
        :return:
        """
        return self._context


