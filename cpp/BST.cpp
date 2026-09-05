#include "BST.h"
#include <fstream>
#include <sstream>
#include <vector>

BST::BST() : root(nullptr) {}

BST::~BST() {
    destroyHelper(root);
}

void BST::destroyHelper(TreeNode* node) {
    if (node == nullptr) return;
    destroyHelper(node->left);
    destroyHelper(node->right);
    delete node;
}

TreeNode* BST::insertHelper(TreeNode* node, const Account& acc) {
    if (node == nullptr) {
        return new TreeNode(acc);
    }
    if (acc.id < node->data.id) {
        node->left = insertHelper(node->left, acc);
    } else if (acc.id > node->data.id) {
        node->right = insertHelper(node->right, acc);
    }
    // if acc.id == node->data.id, IDs must be unique, so we just ignore
    // the duplicate insert (caller should check search() first).
    return node;
}

void BST::insert(const Account& acc) {
    root = insertHelper(root, acc);
}

TreeNode* BST::searchHelper(TreeNode* node, int id) {
    if (node == nullptr) return nullptr;
    if (id == node->data.id) return node;
    if (id < node->data.id) return searchHelper(node->left, id);
    return searchHelper(node->right, id);
}

Account* BST::search(int id) {
    TreeNode* found = searchHelper(root, id);
    return found ? &(found->data) : nullptr;
}

void BST::findMaxIdHelper(TreeNode* node, int& currentMax) {
    if (node == nullptr) return;
    if (node->data.id > currentMax) currentMax = node->data.id;
    findMaxIdHelper(node->left, currentMax);
    findMaxIdHelper(node->right, currentMax);
}

int BST::getNextId() {
    int maxId = 1000; // first generated ID will be 1001
    findMaxIdHelper(root, maxId);
    return maxId + 1;
}

void BST::inorderSaveHelper(TreeNode* node, std::string& outBuffer) {
    if (node == nullptr) return;
    inorderSaveHelper(node->left, outBuffer);

    outBuffer += std::to_string(node->data.id);
    outBuffer += "|";
    outBuffer += node->data.name;
    outBuffer += "|";
    outBuffer += node->data.password;
    outBuffer += "|";
    outBuffer += std::to_string(node->data.balance);
    outBuffer += "|";
    outBuffer += accountTypeToString(node->data.type);
    outBuffer += "\n";

    inorderSaveHelper(node->right, outBuffer);
}

void BST::saveToFile(const std::string& filename) {
    std::string buffer;
    inorderSaveHelper(root, buffer);

    std::ofstream out(filename, std::ios::trunc);
    out << buffer;
    out.close();
}

// Splits a line on '|' into its fields.
static std::vector<std::string> splitLine(const std::string& line) {
    std::vector<std::string> fields;
    std::stringstream ss(line);
    std::string field;
    while (std::getline(ss, field, '|')) {
        fields.push_back(field);
    }
    return fields;
}

void BST::loadFromFile(const std::string& filename) {
    std::ifstream in(filename);
    if (!in.is_open()) {
        return; // no existing data file yet -- start with an empty tree
    }

    std::string line;
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::vector<std::string> f = splitLine(line);
        if (f.size() < 5) continue; // malformed line, skip it

        int id = std::stoi(f[0]);
        std::string name = f[1];
        std::string password = f[2];
        double balance = std::stod(f[3]);
        AccountType type = stringToAccountType(f[4]);

        Account acc(name, id, balance, password, type);
        insert(acc);
    }
    in.close();
}
