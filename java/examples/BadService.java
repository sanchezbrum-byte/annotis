// ❌ BAD: This file demonstrates common Java anti-patterns. Do NOT use as a template.
package com.example.orders;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;

// ❌ BAD: no Javadoc, unclear name, not @Service
public class BadService {

  // ❌ BAD: hardcoded credentials in source
  static String DB_URL = "jdbc:mysql://prod-db:3306/orders";
  static String DB_USER = "root";
  static String DB_PASS = "SuperSecret123!"; // ❌ BAD: secret in version control

  // ❌ BAD: creates a connection per call — exhausts connection pool
  private Connection getConnection() throws Exception {
    return DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
  }

  // ❌ BAD: takes Object param, does nothing with errors, too long, many responsibilities
  public Object processOrder(String id, String token) {
    try {
      Connection conn = getConnection();
      Statement stmt = conn.createStatement();

      // ❌ BAD: SQL injection via string concatenation
      ResultSet rs = stmt.executeQuery("SELECT * FROM orders WHERE id = '" + id + "'");

      if (!rs.next()) {
        return null; // ❌ BAD: returning null — causes NullPointerExceptions upstream
      }

      String status = rs.getString("status");
      double total = rs.getDouble("total");

      if (!status.equals("PENDING")) {
        System.out.println("Order not pending"); // ❌ BAD: System.out.println instead of logging
        return null;
      }

      // ❌ BAD: blocking HTTP call with no timeout, no connection reuse
      java.net.URL url = new java.net.URL("https://api.payments.io/charge");
      java.net.HttpURLConnection http = (java.net.HttpURLConnection) url.openConnection();
      http.setRequestMethod("POST");
      http.setRequestProperty("Authorization", "Bearer sk_live_HARDCODED"); // ❌ BAD: secret in code

      // ❌ BAD: ignores HTTP status code
      http.getInputStream();

      // ❌ BAD: SQL injection in UPDATE as well
      stmt.executeUpdate("UPDATE orders SET status='PAID' WHERE id='" + id + "'");

      // ❌ BAD: no conn.close() — resource leak (should use try-with-resources)

      ArrayList result = new ArrayList(); // ❌ BAD: raw ArrayList, no generics
      result.add(id);
      result.add(total);
      return result;

    } catch (Exception e) {
      // ❌ BAD: catches all exceptions, swallows them, returns null silently
      e.printStackTrace(); // ❌ BAD: prints stack trace to stderr instead of logging
      return null;
    }
  }

  // ❌ BAD: static utility method coupling all callers to BadService, not injectable
  public static void cancelOrder(String id) throws Exception {
    Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
    Statement stmt = conn.createStatement();
    // ❌ BAD: SQL injection
    stmt.executeUpdate("DELETE FROM orders WHERE id = '" + id + "'");
    // ❌ BAD: connection never closed
  }
}
