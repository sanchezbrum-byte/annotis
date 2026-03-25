// ❌ BAD: This file demonstrates common Kotlin anti-patterns. Do NOT use as a template.
package com.example.orders

import java.sql.DriverManager

// ❌ BAD: companion object for global-ish mutable state
object Config {
    var dbPassword = "HardcodedPass123!" // ❌ BAD: secret in source, mutable
    var apiKey = "sk_live_HARDCODED_KEY" // ❌ BAD: hardcoded credential
}

// ❌ BAD: data class used as god object — domain model + repo + service mixed
data class BadOrderService(
    val dbUrl: String = "jdbc:mysql://prod:3306/orders" // ❌ BAD: hardcoded prod URL
) {
    // ❌ BAD: public mutable field instead of proper DI
    var paymentUrl = "https://api.payments.io"

    // ❌ BAD: Any return type — no type safety
    fun process(id: Any?, token: Any?): Any? {
        if (id == null) return null // ❌ BAD: returns null instead of throwing or Result

        // ❌ BAD: opens a new DB connection per call — exhausts connection pool
        val conn = DriverManager.getConnection(dbUrl, "root", Config.dbPassword)
        val stmt = conn.createStatement()

        // ❌ BAD: SQL injection via string interpolation
        val rs = stmt.executeQuery("SELECT * FROM orders WHERE id = '$id'")

        if (!rs.next()) return null // ❌ BAD: null instead of sealed class / exception

        val status = rs.getString("status")
        val total = rs.getDouble("total")

        if (status != "PENDING") {
            println("not pending: $status") // ❌ BAD: println in business logic
            return null
        }

        // ❌ BAD: Thread.sleep in business logic — blocking coroutine dispatcher
        Thread.sleep(500)

        try {
            // ❌ BAD: raw URL connection, no timeout, no reuse
            val url = java.net.URL("$paymentUrl/charge")
            val conn2 = url.openConnection() as java.net.HttpURLConnection
            conn2.requestMethod = "POST"
            conn2.setRequestProperty("Authorization", Config.apiKey)
            conn2.connect()
            // ❌ BAD: HTTP status not checked
        } catch (e: Exception) {
            // ❌ BAD: swallows exception, returns null silently
            return null
        }

        // ❌ BAD: SQL injection in UPDATE
        stmt.executeUpdate("UPDATE orders SET status='PAID' WHERE id='$id'")

        // ❌ BAD: connection never closed — resource leak (no use())
        return mapOf("id" to id, "total" to total) // ❌ BAD: untyped Map instead of data class
    }

    // ❌ BAD: suspend function that calls blocking code — will deadlock on confined dispatcher
    suspend fun cancelOrder(id: String) {
        val conn = DriverManager.getConnection(dbUrl, "root", Config.dbPassword) // blocks thread
        val stmt = conn.createStatement()
        stmt.executeUpdate("DELETE FROM orders WHERE id = '$id'") // SQL injection
        // ❌ BAD: conn not closed
    }
}
