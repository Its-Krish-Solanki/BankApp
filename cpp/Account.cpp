#include "Account.h"

std::string accountTypeToString(AccountType type) {
    switch (type) {
        case SAVINGS: return "SAVINGS";
        case CURRENT: return "CURRENT";
        default:      return "SAVINGS";
    }
}

AccountType stringToAccountType(const std::string& str) {
    if (str == "CURRENT") return CURRENT;
    return SAVINGS; // default / fallback
}
