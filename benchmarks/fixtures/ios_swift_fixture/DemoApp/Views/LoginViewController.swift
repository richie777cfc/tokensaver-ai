import UIKit

class LoginViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        let savedToken = UserDefaults.standard.string(forKey: "authToken")
        let env = ProcessInfo.processInfo.environment["API_ENV"]
        let version = Bundle.main.infoDictionary?["CFBundleShortVersionString"]
    }

    func navigateToHome() {
        performSegue(withIdentifier: "showHome", sender: self)
    }
}
