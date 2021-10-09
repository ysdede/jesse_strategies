

@numba.njit
def shift4_numba(arr, num, fill_value=np.nan):
    if num >= 0:
        return np.concatenate((np.full(num, fill_value), arr[:-num]))
    else:
        return np.concatenate((arr[-num:], np.full(-num, fill_value)))


def my_shift(arr, num=1):
    out = np.copy(arr)
    for i in range(arr.size):
        prev = arr[i - num]
        out[i] = arr[i] if np.isnan(prev) else prev
    return out


# @njit
# def var_helper(valpha, chandeMO, source, length):
#     VAR = np.full_like(source, 0.0)
#     for i in range(length, VAR.size):
#         VAR[i] = (valpha * chandeMO[i] * source[i]) + (1 - valpha * chandeMO[i]) * VAR[i - 1]
#     return VAR