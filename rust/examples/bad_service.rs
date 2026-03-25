// ❌ BAD: This file demonstrates common Rust anti-patterns. Do NOT use as a template.
#![allow(dead_code, unused_variables)]

use std::collections::HashMap;

// ❌ BAD: global mutable static — not thread-safe without synchronisation
static mut API_KEY: &str = "sk_live_HARDCODED_KEY"; // ❌ BAD: secret in source

// ❌ BAD: String-typed status — not exhaustive, no compile-time safety
pub struct BadOrder {
    pub id: String,        // ❌ BAD: plain String, no newtype — confusable with user_id
    pub user_id: String,
    pub status: String,    // ❌ BAD: "pending", "paid", etc. as raw strings
    pub total: f64,        // ❌ BAD: f64 for money — floating-point rounding errors
}

// ❌ BAD: function returns Option<String> for errors — no context about what went wrong
pub fn process_payment(order_id: &str, token: &str) -> Option<String> {
    if order_id.is_empty() {
        return None; // ❌ BAD: None gives no error information
    }

    // ❌ BAD: unsafe block to access global mutable static — data race in multithreaded context
    let key = unsafe { API_KEY };

    // ❌ BAD: .unwrap() will panic if the vec is empty — no graceful error handling
    let orders: Vec<BadOrder> = Vec::new();
    let order = orders.iter().find(|o| o.id == order_id).unwrap(); // ❌ BAD: panics

    if order.status != "pending" {
        println!("order not pending"); // ❌ BAD: println! in library code
        return None;
    }

    // ❌ BAD: format! used to build a SQL query — SQL injection if order_id is user-supplied
    let query = format!("SELECT * FROM payments WHERE order_id = '{}'", order_id);

    // ❌ BAD: clone everywhere to avoid understanding ownership
    let token_copy = token.to_string().clone(); // ❌ BAD: redundant .to_string().clone()
    let id_copy = order_id.to_owned().clone();  // ❌ BAD: redundant .to_owned().clone()

    // ❌ BAD: Box<dyn std::error::Error> as return type on public API — opaque to callers
    // Should use thiserror or a concrete enum.

    Some("fake-payment-id".to_string())
}

// ❌ BAD: using String keys and dynamic dispatch (HashMap<String, Box<dyn Any>>) 
// instead of typed structs — loses compile-time guarantees
pub fn get_order_details(id: &str) -> HashMap<String, String> {
    let mut map = HashMap::new();
    map.insert("id".to_string(), id.to_string());
    // ❌ BAD: missing fields silently omitted — caller doesn't know what's present
    map
}

// ❌ BAD: mixing sync I/O inside an async fn — will block the executor thread
pub async fn fetch_and_cancel(order_id: &str) {
    // ❌ BAD: std::thread::sleep blocks the async executor, starving other tasks
    std::thread::sleep(std::time::Duration::from_secs(2));
    // Should use: tokio::time::sleep(Duration::from_secs(2)).await;
    println!("cancelled {}", order_id);
}
