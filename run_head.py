import numpy as np
import lib.funcs.dat_io as io
import CLLAMA
from streamlit import caching

values = np.arange(0.3, 1.75, 0.05)

for value in values:

    sfwfval = value

    if value > 0:
        sign = "+"
    else:
        sign = "-"

    sfwflabel = f"sfwf7{value}"

    print(f"Running CCLAMA with value: {value}")

    io.save(".", "sfwfval", sfwfval)
    io.save(".", "sfwflabel", sfwflabel)
    CLLAMA.main()
    caching.clear_cache()
