import Foundation

class APIService {
    let baseURL = "https://api.example.com/v1"

    func fetchUsers() {
        let url = URL(string: "https://api.example.com/v1/users")!
        URLSession.shared.dataTask(with: url) { data, response, error in
        }.resume()
    }

    func fetchPosts() {
        let url = URL(string: "https://api.example.com/v1/posts")!
        URLSession.shared.dataTask(with: url) { data, response, error in
        }.resume()
    }

    func login(email: String, password: String) {
        let url = URL(string: "https://api.example.com/v1/auth/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
    }
}
