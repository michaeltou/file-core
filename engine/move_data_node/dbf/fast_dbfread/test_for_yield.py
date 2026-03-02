def count_up_to(max):
    count = 1
    while count <= max:
        yield count  # 每次执行到这里暂停，返回count的值
        count += 1

# 使用生成器
counter = count_up_to(5)
print(counter)
print('Before yielding')
print(next(counter))  # 输出: 1
print(next(counter))  # 输出: 2
print(counter.__next__())  # 输出: 3