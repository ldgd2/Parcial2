import 'package:flutter/material.dart';
import '../../../../../core/network/api_client.dart';
import '../../../../../core/storage/local_storage.dart';
import '../../../vehicles/data/vehicle_service.dart';
import '../../../emergencies/data/emergency_service.dart';

class HomeController extends ChangeNotifier {
  List<Map<String, dynamic>> vehicles = [];
  List<Map<String, dynamic>> emergencies = [];
  bool isLoading = false;
  late final VehicleService _vehicleService;
  late final EmergencyService _emergencyService;

  HomeController() {
    final storage = LocalStorage();
    final apiClient = ApiClient(localStorage: storage);
    _vehicleService = VehicleService(apiClient: apiClient);
    _emergencyService = EmergencyService(apiClient: apiClient);
    loadData();
  }

  Future<void> loadData() async {
    isLoading = true;
    notifyListeners();

    try {
      final results = await Future.wait([
        _vehicleService.getMyVehicles(),
        _emergencyService.getHistory(),
      ]);
      vehicles = results[0];
      emergencies = results[1];
    } catch (e) {
      debugPrint('Error loading home data: $e');
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
