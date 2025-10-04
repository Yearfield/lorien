import importlib.util

spec = importlib.util.spec_from_file_location('helpers','api/routers/helpers.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
coerce = helpers.coerce_rows_to_canonical

rows=[{"D0":"Root A","D1":"Parent","D2":"child1","D3":"","D4":"","D5":"","D6":"","Notes":""}]
print(coerce(rows))

rows2=[{"D0":"Root A","D1":"Parent","D2":"child1"}]
print(coerce(rows2))

rows3=[{"Vital Measurement":"Root A","Parent":"Parent","child1":"child1","Notes":"N"}]
print(coerce(rows3))

rows4=[{"D0":"Root A","D1":"Parent","D2":"child1","Actions":"Act"}]
print(coerce(rows4))

