/**
 * ❌ BAD EXAMPLE — Do NOT follow this code.
 * Every violation is annotated.
 */

var db = require('./db') // ❌ BAD: var instead of const; CommonJS require mixed with bad style
var stripe = require('stripe')('sk_live_HARDCODED_KEY_HERE') // ❌ BAD: hardcoded live secret key

// ❌ BAD: global mutable state — causes test pollution and concurrency bugs
var currentUser = null
var orderCache = {}

// ❌ BAD: function name is vague — what does "process" mean here?
// ❌ BAD: 7 parameters — impossible to call without documentation
// ❌ BAD: no JSDoc at all
function process(u, items, c, tok, d, addr, note) {
  // ❌ BAD: single-letter parameter names — u? c? d? incomprehensible
  // ❌ BAD: no input validation at all

  if (u != null) { // ❌ BAD: use === not loose equality (eqeqeq rule)
    if (items.length > 0) {
      if (c == 'USD' || c == 'EUR') { // ❌ BAD: loose equality
        // ❌ BAD: deep nesting — use early returns
        if (tok != '') {

          // ❌ BAD: synchronous blocking database call — no async/await
          var result = db.querySync("SELECT * FROM users WHERE id = '" + u + "'")
          // ❌ BAD CRITICAL: SQL injection — string concatenation in SQL query
          // ❌ BAD: no error handling for database call

          // ❌ BAD: console.log in production code — use a logger
          console.log('got user', result)

          // ❌ BAD: commented-out dead code
          // var oldResult = db.querySync("SELECT * FROM users where id = " + u)

          var total = 0
          // ❌ BAD: traditional for loop when forEach/reduce is cleaner
          for (var i = 0; i < items.length; i++) {
            // ❌ BAD: accessing .price without any null/undefined check
            total = total + items[i].price * items[i].qty
          }

          // ❌ BAD: no try/catch — unhandled promise rejection
          // ❌ BAD: fire-and-forget without awaiting or handling
          stripe.charges.create({
            amount: total,
            currency: c,
            source: tok
            // ❌ BAD: no idempotency key — double-charges on retry
          }).then(function(charge) {
            // ❌ BAD: nested .then() chains — callback hell
            db.querySync("UPDATE orders SET status = 'paid' WHERE user = '" + u + "'")
            // ❌ BAD CRITICAL: SQL injection again
            console.log('charged!', charge.id) // ❌ BAD: console.log
          })

          // ❌ BAD: returning before the async operation completes
          // ❌ BAD: returns different types (object on success, nothing on failure)
          return { ok: true, user: result, amount: total }
        }
      }
    }
  }
  // ❌ BAD: implicit undefined return — caller cannot distinguish success from failure
}

// ❌ BAD: PascalCase for a plain function (not a class)
// ❌ BAD: modifies global state
function SetCurrentUser(userId) {
  // ❌ BAD: no type checking, no validation
  currentUser = userId // ❌ BAD: mutating global variable
}

// ❌ BAD: function does two things — fetches AND formats (SRP violation)
// ❌ BAD: no error handling, no types
function getOrdersAndFormat(uid) {
  var orders = db.querySync("SELECT * FROM orders WHERE user_id = " + uid)
  // ❌ BAD: SQL injection — unparameterized uid

  var str = '' // ❌ BAD: `str` is meaningless
  for (var j = 0; j < orders.length; j++) {
    str = str + orders[j].id + ',' + orders[j].total + '\n'
    // ❌ BAD: string concatenation in loop = O(n²)
  }
  return str
}

// ❌ BAD: using eval with user input = arbitrary code execution (RCE)
function applyDiscount(order, discountExpr) {
  var discountFn = eval('(' + discountExpr + ')') // ❌ CRITICAL: eval of user input
  return order.total - discountFn(order.total)
}
