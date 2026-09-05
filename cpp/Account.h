#ifndef ACCOUNT_H
#define ACCOUNT_H

#include <string>

enum AccountType {
    SAVINGS,
    CURRENT
};

std::string accountTypeToString(AccountType type);

AccountType stringToAccountType(const std::string& str);

struct Account {
    std::string name;
    int id;
    double balance;
    std::string password;
    AccountType type;

    Account()
        : name(""), id(0), balance(0.0), password(""), type(SAVINGS) {}

    Account(const std::string& name_, int id_, double balance_,
            const std::string& password_, AccountType type_)
        : name(name_), id(id_), balance(balance_),
          password(password_), type(type_) {}
};

#endif 
