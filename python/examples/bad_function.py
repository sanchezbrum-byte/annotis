"""
❌ BAD EXAMPLE — Do NOT follow this code.

Each violation is annotated with a comment explaining the specific problem
and a reference to the rule that is violated.
"""

import requests
import json, sys  # ❌ BAD: multiple imports on one line (PEP 8 §Imports)
from datetime import *  # ❌ BAD: wildcard import — pollutes namespace (PEP 8)

db = None  # ❌ BAD: global mutable state — causes bugs in concurrent code and tests
SECRET_KEY = "s3cr3t_k3y_abc123"  # ❌ BAD: hardcoded secret (OWASP A02, security.md)
stripe_key = "sk_live_AbCdEfGhIjKlMnOpQrStUvWx"  # ❌ BAD: hardcoded live API key

# ❌ BAD: no type annotations anywhere in this file
# ❌ BAD: no module-level docstring explaining purpose
def process(u, a, c, tok, disc, ship, note):  # ❌ BAD: 7 parameters (max is 5)
    # ❌ BAD: single-letter names — meaningless outside this line
    # ❌ BAD: no docstring at all

    # ❌ BAD: business logic mixed with persistence and HTTP in one function (SRP violation)
    # ❌ BAD: no input validation before using values

    if u != None:  # ❌ BAD: use `is not None`, not `!= None` (PEP 8)
        if a > 0:
            if c == "USD" or c == "EUR":  # ❌ BAD: deep nesting (use early returns)
                if tok != "":
                    # ❌ BAD: string formatting in SQL = SQL injection vulnerability
                    query = "SELECT * FROM users WHERE id = '" + u + "'"
                    result = db.execute(query)  # ❌ BAD: unparameterized query

                    # ❌ BAD: commented-out dead code — delete it or use git history
                    # old_result = db.execute("SELECT * FROM users WHERE id = %s", u)

                    usr_obj = result.fetchone()  # ❌ BAD: opaque abbreviation

                    # ❌ BAD: no None check — will crash with AttributeError
                    if usr_obj["active"] == 1:
                        # ❌ BAD: string concatenation in loop (O(n²) for large orders)
                        item_str = ""
                        for i in usr_obj["items"]:
                            item_str = item_str + str(i) + ","

                        # ❌ BAD: catching bare Exception and silently ignoring it
                        try:
                            r = requests.post(  # ❌ BAD: no timeout specified
                                "https://api.stripe.com/v1/charges",
                                data={
                                    "amount": a,
                                    "currency": c,
                                    "source": tok,
                                    "api_key": stripe_key,  # ❌ BAD: secret in request body
                                },
                            )
                            # ❌ BAD: no error status check; assumes 200
                            data = json.loads(r.text)
                            print(f"Charge result: {data}")  # ❌ BAD: print in production code
                            # ❌ BAD: no logging, no audit trail
                        except:  # ❌ BAD: bare except — swallows ALL exceptions silently
                            pass  # ❌ BAD: silent error swallowing

                        # ❌ BAD: raw SQL with string formatting = SQL injection
                        db.execute(
                            f"UPDATE users SET balance = balance - {a} WHERE id = '{u}'"
                        )

                        # ❌ BAD: returns different types (dict vs None) — unpredictable
                        return {"status": "ok", "user": u, "amount": a}

    # ❌ BAD: implicit None return when conditions aren't met — caller can't distinguish
    # success from failure without checking for None


def DoTheThing(X):  # ❌ BAD: PascalCase for function (use snake_case), vague name
    # ❌ BAD: no type annotation, no docstring
    temp = []  # ❌ BAD: `temp` is a meaningless name
    for i in range(0, len(X)):  # ❌ BAD: use `for item in X` or `enumerate(X)`
        if X[i] != None:
            temp.append(X[i])
    return temp


# ❌ BAD: function name describes implementation detail, not behavior
def send_email_via_smtp_server(e, s, b):
    # ❌ BAD: abbreviations for all params — what is `e`? `s`? `b`?
    import smtplib  # ❌ BAD: import inside function (slow, hides dependencies)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    # ❌ BAD: hardcoded SMTP credentials
    server.login("myapp@gmail.com", "gmail_app_password_here")
    server.sendmail("myapp@gmail.com", e, b)
    server.quit()


class user:  # ❌ BAD: class name must be PascalCase (User, not user) (PEP 8)
    # ❌ BAD: no type annotations, no docstring

    def __init__(self):
        self.data = {}  # ❌ BAD: `data` is meaningless — what kind of data?

    # ❌ BAD: function does save AND send email — two responsibilities (SRP)
    def save_and_notify(self):
        db.execute(f"INSERT INTO users VALUES ('{self.data['email']}')")  # ❌ SQLi
        send_email_via_smtp_server(self.data["email"], "Welcome", "Hi!")
