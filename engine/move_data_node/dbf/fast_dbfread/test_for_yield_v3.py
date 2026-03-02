def count_up_to(max):
    count = 1
    while count <= max:
        yield count  # 每次执行到这里暂停，返回count的值
        count += 1

# 使用生成器
for count in count_up_to(5):
    print(count)

mylist = list(count_up_to(5))
print(mylist)




