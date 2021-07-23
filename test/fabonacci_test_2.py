#%%
def fabonacci(numb:int) -> int:
    if numb <= 1:
        return numb
    else:
        return fabonacci(numb-1) + fabonacci(numb-2)
#%%
#%%
for i in range(21):
    print(f"Fabonacci an der Stelle {i}: {fabonacci(i)}")
#%%