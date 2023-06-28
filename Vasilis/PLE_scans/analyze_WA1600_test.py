import matplotlib.pyplot as plt
from functions26.filing.QDLFiling import MultiQDLF


file = MultiQDLF.load('test2WA1600.mqdlf')

print(file.data_managers)

x_data = file.data_managers[0].data['x1']
y_data = file.data_managers[0].data['y1']
plt.plot(x_data, y_data)
plt.show()
