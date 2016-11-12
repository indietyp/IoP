import matplotlib.pyplot as plt

output = []
i = 0
while sum(output) < 10000:
  i += 1
  output.append(5 + int(i**2.2))

print(i)
print(sum(output))
print(output)

plt.plot(output)
plt.ylabel('some numbers')
plt.show()
