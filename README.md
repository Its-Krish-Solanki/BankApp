A simple banking app with a C++ backend (account data + binary search
tree for storage/lookup) and a Python Tkinter frontend (GUI).

```
banking_app/
├── cpp/
│   ├── Account.h      # struct Account + enum AccountType (blueprint for an account)
│   ├── Account.cpp     # enum <-> string helpers
│   ├── BST.h            # binary search tree that stores accounts, keyed by ID
│   ├── BST.cpp
│   └── main.cpp        # CLI backend: create / find / auth / deposit / withdraw
├── python/
│   └── bank_gui.py     # Tkinter GUI (talks to the compiled backend via subprocess)
├── data/
│   └── accounts.dat    # generated automatically the first time you create an account
├── Makefile
└── README.md
```

bash
cd banking_app
make

bash
g++ -std=c++17 -Wall -o bank_app cpp/main.cpp cpp/Account.cpp cpp/BST.cpp

python3 python/bank_gui.py
