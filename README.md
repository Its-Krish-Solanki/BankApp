A simple banking app with a C++ backend (account data + binary search
tree for storage/lookup) and a Python Tkinter frontend (GUI).

```
banking_app/
├── cpp/
│   ├── Account.h      
│   ├── Account.cpp     
│   ├── BST.h            
│   ├── BST.cpp
│   └── main.cpp        
├── python/
│   └── bank_gui.py     
├── data/
│   └── accounts.dat    
├── Makefile
└── README.md
```

bash
cd banking_app
make

bash
g++ -std=c++17 -Wall -o bank_app cpp/main.cpp cpp/Account.cpp cpp/BST.cpp

python3 python/bank_gui.py
