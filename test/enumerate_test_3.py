#%%
def my_enumerate(my_list):
    i = 0
    ite = iter(my_list)
    while True:
        try:
            yield (i, next(ite))
            i += 1
        except StopIteration:
            break
#%%
#%%
list_connected = my_enumerate(["hey", "was", "geht"])

for i in list_connected:
    print(i)
#%%