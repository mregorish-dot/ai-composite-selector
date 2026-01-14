import UIKit
import WebKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    
    var window: UIWindow?
    
    // ЗАМЕНИТЕ НА ВАШУ ССЫЛКУ НА STREAMLIT CLOUD
    private static let APP_URL = "https://ВАШ_ПОЛЬЗОВАТЕЛЬ-streamlit-app-XXXXXX.streamlit.app"
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        window = UIWindow(frame: UIScreen.main.bounds)
        
        let webView = WKWebView(frame: window!.bounds)
        webView.navigationDelegate = self
        
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        
        let viewController = UIViewController()
        viewController.view = webView
        
        if let url = URL(string: AppDelegate.APP_URL) {
            let request = URLRequest(url: url)
            webView.load(request)
        }
        
        window?.rootViewController = viewController
        window?.makeKeyAndVisible()
        
        return true
    }
}

extension AppDelegate: WKNavigationDelegate {
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        print("Page loaded successfully")
    }
    
    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        print("Failed to load page: \(error.localizedDescription)")
    }
}

