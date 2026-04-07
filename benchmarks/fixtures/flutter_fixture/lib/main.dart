import 'package:flutter/widgets.dart';

import 'navigation/app_pages.dart';
import 'services/api_client.dart';
import 'services/remote_config_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  final client = ApiClient();
  client.ping();
  RemoteConfigService.get().getString('welcome_title');
  runApp(const Placeholder());
}
