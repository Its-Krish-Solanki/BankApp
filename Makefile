CXX = g++
CXXFLAGS = -std=c++17 -Wall -O2
SRC = cpp/main.cpp cpp/Account.cpp cpp/BST.cpp
TARGET = bank_app

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)
	rm -f data/accounts.dat

.PHONY: all clean
