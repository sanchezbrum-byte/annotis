// ❌ BAD: This file demonstrates common C++ anti-patterns. Do NOT use as a template.

#include <cstdio>
#include <cstring>
#include <iostream>
#include <string>

// ❌ BAD: global mutable state — not thread-safe
const char* g_api_key = "sk_live_HARDCODED_KEY"; // ❌ BAD: secret in source
static int  g_order_count = 0;                    // ❌ BAD: global counter

// ❌ BAD: raw pointer ownership with manual new/delete — memory leak risk
struct Order {
    char* id;       // ❌ BAD: raw char* instead of std::string
    double total;   // ❌ BAD: double for money — floating-point errors
    char* status;   // ❌ BAD: raw char* for status instead of enum
};

// ❌ BAD: factory returns raw pointer — caller must remember to delete
Order* create_order(const char* id, double total) {
    Order* o = new Order(); // ❌ BAD: raw new — must be manually deleted
    o->id = strdup(id);     // ❌ BAD: strdup returns malloc'd memory, no RAII
    o->total = total;
    o->status = strdup("pending");
    g_order_count++;
    return o;               // ❌ BAD: ownership transfer unclear
}

// ❌ BAD: throws generic std::exception in hot path — no typed error info
// ❌ BAD: takes raw pointer — ownership semantics unclear
bool process_payment(Order* order, const char* token) {
    if (order == nullptr) {
        throw std::exception(); // ❌ BAD: too generic, no message
    }

    // ❌ BAD: strcmp for equality — error-prone, no null check
    if (strcmp(order->status, "pending") != 0) {
        std::cout << "not pending" << std::endl; // ❌ BAD: std::cout in library code
        return false;
    }

    // ❌ BAD: sprintf with user-supplied data — buffer overflow if id is long
    char query[64];
    sprintf(query, "SELECT * FROM orders WHERE id = '%s'", order->id); // ❌ BAD: SQL injection + overflow

    // ❌ BAD: printf for logging — no timestamp, no level, not structured
    printf("processing order %s\n", order->id);

    // ❌ BAD: using global API key
    printf("using key: %s\n", g_api_key);

    return true;
    // ❌ BAD: free(order->id) never called — memory leak
    // ❌ BAD: order is never deleted — memory leak
}

// ❌ BAD: C-style cast instead of static_cast / reinterpret_cast
void update_status(Order* order, void* new_status) {
    order->status = (char*)new_status; // ❌ BAD: C-style cast, aliasing issues
}

// ❌ BAD: No virtual destructor — UB when deleting derived through base pointer
class BaseService {
public:
    virtual void Process() {}
    ~BaseService() {} // ❌ BAD: must be virtual ~BaseService()
};

class DerivedService : public BaseService {
    int* resource = new int(42); // ❌ BAD: raw new in member, no destructor
public:
    void Process() override {}
    // ❌ BAD: no destructor — resource leaked when deleted via BaseService*
};
