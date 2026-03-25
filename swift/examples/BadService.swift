// ❌ BAD: This file demonstrates common Swift anti-patterns. Do NOT use as a template.
import Foundation

// ❌ BAD: global mutable state — not Sendable, not thread-safe
var globalApiKey = "sk_live_HARDCODED_KEY" // ❌ BAD: hardcoded secret
var currentOrder: [String: Any]? = nil      // ❌ BAD: untyped dictionary as model

// ❌ BAD: class when struct would be better; no final; no DI
class BadOrderService {

    // ❌ BAD: hardcoded URL, concrete URLSession (untestable)
    let session = URLSession.shared
    let paymentUrl = "https://api.payments.io" // ❌ BAD: magic string

    // ❌ BAD: returning optional Any — caller has no type information
    // ❌ BAD: completion handler instead of async/await (legacy pattern)
    func processOrder(id: String?, token: String?, completion: @escaping (Any?) -> Void) {
        guard let id = id else {
            completion(nil) // ❌ BAD: nil instead of typed error
            return
        }

        // ❌ BAD: force unwrap — will crash at runtime if url is nil
        let url = URL(string: "\(paymentUrl)/charge?id=\(id)")! // ❌ BAD: URL-encodes user input improperly

        var request = URLRequest(url: url)
        request.setValue(globalApiKey, forHTTPHeaderField: "Authorization") // ❌ BAD: uses global

        // ❌ BAD: no error handling on URLSession response
        session.dataTask(with: request) { data, _, _ in // ❌ BAD: ignores error and response
            guard let data = data else {
                completion(nil) // ❌ BAD: swallows network error silently
                return
            }

            // ❌ BAD: force try — will crash on malformed JSON
            let result = try! JSONSerialization.jsonObject(with: data)

            // ❌ BAD: UI update not dispatched to main thread
            completion(result)
        }.resume()
    }

    // ❌ BAD: async function uses Thread.sleep — blocks the cooperative thread pool
    func cancelOrder(id: String) async {
        Thread.sleep(forTimeInterval: 2.0) // ❌ BAD: use try await Task.sleep(...)
        print("cancelled \(id)")           // ❌ BAD: print() in production code
    }

    // ❌ BAD: ! force-unwrap throughout
    func getOrderTotal(id: String) -> Double {
        let dict = currentOrder! as! [String: Double] // ❌ BAD: double force-cast; uses global
        return dict["total"]! // ❌ BAD: crashes if key missing
    }
}
