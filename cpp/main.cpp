#include "Account.h"
#include "BST.h"
#include <iostream>
#include <string>
#include <cstdlib>

static const std::string DATA_FILE = "data/accounts.dat";

static void printFail(const std::string& reason) {
    std::cout << "FAIL|" << reason << std::endl;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printFail("No command given");
        return 1;
    }

    std::string command = argv[1];

    BST tree;
    tree.loadFromFile(DATA_FILE);

    if (command == "create") {
        if (argc < 6) { printFail("Usage: create <name> <password> <type> <balance>"); return 1; }
        std::string name = argv[2];
        std::string password = argv[3];
        AccountType type = stringToAccountType(argv[4]);
        double balance = std::atof(argv[5]);

        if (name.empty() || password.empty()) {
            printFail("Name and password are required");
            return 1;
        }
        if (balance < 0) {
            printFail("Initial balance cannot be negative");
            return 1;
        }

        int newId = tree.getNextId();
        Account acc(name, newId, balance, password, type);
        tree.insert(acc);
        tree.saveToFile(DATA_FILE);

        std::cout << "SUCCESS|" << newId << "|" << name << "|"
                   << balance << "|" << accountTypeToString(type) << std::endl;
        return 0;
    }

    if (command == "find") {
        if (argc < 3) { printFail("Usage: find <id>"); return 1; }
        int id = std::atoi(argv[2]);
        Account* acc = tree.search(id);
        if (acc == nullptr) {
            printFail("Account not found");
            return 0;
        }
        std::cout << "SUCCESS|" << acc->id << "|" << acc->name << "|"
                   << accountTypeToString(acc->type) << std::endl;
        return 0;
    }

    if (command == "auth") {
        if (argc < 4) { printFail("Usage: auth <id> <password>"); return 1; }
        int id = std::atoi(argv[2]);
        std::string password = argv[3];

        Account* acc = tree.search(id);
        if (acc == nullptr) {
            printFail("Account not found");
            return 0;
        }
        if (acc->password != password) {
            printFail("Incorrect password");
            return 0;
        }
        std::cout << "SUCCESS|" << acc->id << "|" << acc->name << "|"
                   << acc->balance << "|" << accountTypeToString(acc->type) << std::endl;
        return 0;
    }

    if (command == "deposit" || command == "withdraw") {
        if (argc < 5) { printFail("Usage: " + command + " <id> <password> <amount>"); return 1; }
        int id = std::atoi(argv[2]);
        std::string password = argv[3];
        double amount = std::atof(argv[4]);

        Account* acc = tree.search(id);
        if (acc == nullptr) {
            printFail("Account not found");
            return 0;
        }
        if (acc->password != password) {
            printFail("Incorrect password");
            return 0;
        }
        if (amount <= 0) {
            printFail("Amount must be positive");
            return 0;
        }

        if (command == "deposit") {
            acc->balance += amount;
        } else { // withdraw
            if (amount > acc->balance) {
                printFail("Insufficient funds");
                return 0;
            }
            acc->balance -= amount;
        }

        tree.saveToFile(DATA_FILE);
        std::cout << "SUCCESS|" << acc->balance << std::endl;
        return 0;
    }

    printFail("Unknown command: " + command);
    return 1;
}
