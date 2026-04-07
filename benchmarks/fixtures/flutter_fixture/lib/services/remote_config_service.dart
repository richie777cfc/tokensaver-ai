class RemoteConfigService {
  static final Map<String, dynamic> _defaults = {
    'welcome_title': 'Hello',
    'show_banner': true,
    'max_cards': 3,
  };

  static RemoteConfigService get() => RemoteConfigService();

  String getString(String key) => _defaults[key] as String? ?? '';
  bool getBool(String key) => _defaults[key] as bool? ?? false;
}
