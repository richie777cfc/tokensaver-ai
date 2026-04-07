import 'app_routes.dart';

class HomePage {}

class DetailsPage {}

class GetPage {
  final String name;
  final dynamic Function() page;

  GetPage({required this.name, required this.page});
}

final appPages = [
  GetPage(name: AppRoutes.home, page: () => HomePage()),
  GetPage(name: AppRoutes.details, page: () => DetailsPage()),
];
