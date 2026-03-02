from engine.core.context import Context


context = Context()

context.set("name", "John")
context.set("age", 30)
context.set("[fund_id]",1234)
context.set("[business_date]",20241205)

print(context.get("name"))
print(context.get("age"))

if '[fund_id]' in context:
    print('[fund_id] is in context')
else:
    print('[fund_id] is not in context')
