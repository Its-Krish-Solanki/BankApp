#ifndef BST_H
#define BST_H

#include "Account.h"
#include <string>

struct TreeNode {
    Account data;
    TreeNode* left;
    TreeNode* right;

    explicit TreeNode(const Account& acc)
        : data(acc), left(nullptr), right(nullptr) {}
};

class BST {
private:
    TreeNode* root;

    TreeNode* insertHelper(TreeNode* node, const Account& acc);
    TreeNode* searchHelper(TreeNode* node, int id);
    void inorderSaveHelper(TreeNode* node, std::string& outBuffer);
    void destroyHelper(TreeNode* node);
    void findMaxIdHelper(TreeNode* node, int& currentMax);

public:
    BST();
    ~BST();

    // Inserts a new account into the tree, keyed by acc.id.
    void insert(const Account& acc);

    // Returns a pointer to the Account with the given id, or nullptr
    // if no such account exists. The pointer is owned by the tree.
    Account* search(int id);

    // Loads all accounts from a flat data file into the tree.
    // File format: one account per line, fields separated by '|':
    //   id|name|password|balance|type
    void loadFromFile(const std::string& filename);

    // Writes every account currently in the tree back out to the data
    // file (in-order traversal), overwriting whatever was there before.
    void saveToFile(const std::string& filename);

    // Scans the tree and returns (max existing id) + 1, used to assign
    // a fresh unique ID to a newly created account. Starts at 1001 if
    // the tree is empty.
    int getNextId();
};

#endif // BST_H
