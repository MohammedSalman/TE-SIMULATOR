exp = 1
alist = [1, 1, 1, 1, 1]
ratios_list = [n for n in range(len(alist))]
ratios_list = [(n + 1) ** exp for n in range(len(alist))]
ratios_list = [n / sum(ratios_list) for n in ratios_list]
ratios_list.reverse()
print(ratios_list)
