// ❌ BAD: This file demonstrates common Go anti-patterns. Do NOT use as a template.
package orders

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"io/ioutil"  // ❌ BAD: ioutil is deprecated since Go 1.16
	"log"
	"net/http"
)

// ❌ BAD: global mutable state — not safe for concurrent use
var db *sql.DB
var apiKey = "sk_live_HARDCODED_SECRET_abc123" // ❌ BAD: hardcoded secret in source

// ❌ BAD: struct with no encapsulation, exported everything, mixing concerns
type OrderProcessor struct {
	DB      *sql.DB      // ❌ BAD: exposed db handle — direct infrastructure dependency
	HttpCli *http.Client // ❌ BAD: concrete type, not interface — untestable
	ApiKey  string
}

// ❌ BAD: function does too many things (SRP violation), poor naming, no docs
func (p *OrderProcessor) DoOrder(id string, token string) map[string]interface{} {
	// ❌ BAD: fmt.Sprintf for SQL query — SQL injection vulnerability
	row := p.DB.QueryRow(fmt.Sprintf("SELECT * FROM orders WHERE id = '%s'", id))

	var orderId, userId, status string
	var total float64
	err := row.Scan(&orderId, &userId, &total, &status)
	if err != nil {
		log.Println("error:", err) // ❌ BAD: log.Println — no structured logging, swallows context
		return nil                 // ❌ BAD: returns nil map — caller cannot distinguish "not found" vs error
	}

	if status != "pending" {
		// ❌ BAD: returning a raw error message as a map key — not typed, not testable
		return map[string]interface{}{"error": "order not pending"}
	}

	// ❌ BAD: no timeout on HTTP request
	req, _ := http.NewRequest("POST", "https://api.payments.io/charge", nil) // ❌ BAD: ignoring error
	req.Header.Set("Authorization", apiKey)                                   // ❌ BAD: uses package-level global
	resp, err := p.HttpCli.Do(req)
	if err != nil {
		panic(err) // ❌ BAD: panic in business logic — will crash the server
	}
	defer resp.Body.Close()

	// ❌ BAD: ioutil.ReadAll is deprecated; also ignoring possible read error
	body, _ := ioutil.ReadAll(resp.Body)

	var result map[string]interface{}
	json.Unmarshal(body, &result) // ❌ BAD: ignoring unmarshal error

	// ❌ BAD: raw SQL with string interpolation — second SQL injection in same function
	p.DB.Exec(fmt.Sprintf("UPDATE orders SET status='paid' WHERE id='%s'", id))

	fmt.Println("done processing order", id) // ❌ BAD: fmt.Println in library code

	return result // ❌ BAD: returning untyped map — caller has no compile-time safety
}

// ❌ BAD: exported global function using package-level db — untestable, not concurrent-safe
func GetAllOrders() []map[string]interface{} {
	rows, err := db.Query("SELECT * FROM orders") // ❌ BAD: uses global db
	if err != nil {
		return nil // ❌ BAD: silently swallows error
	}
	defer rows.Close()

	var results []map[string]interface{}
	for rows.Next() {
		var id, status string
		var total float64
		rows.Scan(&id, &status, &total) // ❌ BAD: ignoring Scan error
		results = append(results, map[string]interface{}{
			"id":     id,
			"status": status,
			"total":  total,
		})
	}
	// ❌ BAD: rows.Err() is never checked
	return results
}
