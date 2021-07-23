#%%
def fabonacci(numb:int) -> int:
    if numb <= 1:
        return numb
    else:
        return fabonacci(numb-1) + fabonacci(numb-2)
#%%#%%
for i in range(10):
    f = fabonacci(i)
    print(f"Fabonacci an Stelle {i}: {f}")
#%%#%%
for i in range(50):
    f = fabonacci(i)
    print(f"Fabonacci an Stelle {i}: {f}")
#%%