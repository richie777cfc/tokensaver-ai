class ApiClient {
  static const String statusUrl = 'https://example.com/api/status';
  static const String loginEndpoint = 'https://example.com/api/login';

  void ping() {
    final request = {
      'path': 'https://example.com/api/ping',
    };
    request.toString();
  }
}
