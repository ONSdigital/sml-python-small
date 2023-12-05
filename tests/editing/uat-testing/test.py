from datatest import validate
data = ['A', 'B', 'C']
requirement = {'A', 'B', 'C', 'D'}
print(validate.superset(data, requirement))