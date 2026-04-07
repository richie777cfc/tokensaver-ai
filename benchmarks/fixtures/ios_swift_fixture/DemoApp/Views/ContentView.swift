import SwiftUI

struct ContentView: View {
    @AppStorage("username") var username = ""
    @AppStorage("isDarkMode") var isDarkMode = false

    var body: some View {
        NavigationView {
            VStack {
                NavigationLink(destination: ProfileView()) {
                    Text("Go to Profile")
                }
                NavigationLink(destination: SettingsView()) {
                    Text("Settings")
                }
            }
        }
    }
}

struct ProfileView: View {
    var body: some View {
        Text("Profile")
    }
}

struct SettingsView: View {
    var body: some View {
        Text("Settings")
    }
}
