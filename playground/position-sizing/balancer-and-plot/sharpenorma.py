import jesse.helpers as jh


ratio = -5
ratio_normalized = jh.normalize(ratio, -.5, 5)
for j in range(0, 200):
    i = j/10
    print(f'{i} -> {round(jh.normalize(i, -.5, 5)+4, 3)} | {-i} -> {round(jh.normalize(-i, -.5, 5)+4, 3)}')
