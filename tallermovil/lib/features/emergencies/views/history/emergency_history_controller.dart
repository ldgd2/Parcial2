import 'package:flutter/material.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/storage/local_storage.dart';
import '../../data/emergency_service.dart';

class EmergencyHistoryController extends ChangeNotifier {
  List<Map<String, dynamic>> emergencies = [];
  bool isLoading = false;
  late final EmergencyService _emergencyService;

  EmergencyHistoryController() {
    final storage = LocalStorage();
    final apiClient = ApiClient(localStorage: storage);
    _emergencyService = EmergencyService(apiClient: apiClient);
    loadHistory();
  }

  Future<void> loadHistory() async {
    isLoading = true;
    notifyListeners();

    try {
      final storage = LocalStorage();
      final rol = await storage.getRol();
      
      if (rol == 'tecnico') {
        final codTaller = await storage.getCodTaller();
        if (codTaller != null && codTaller.isNotEmpty) {
          emergencies = await _emergencyService.getTallerHistory(codTaller);
        } else {
          emergencies = [];
        }
      } else {
        emergencies = await _emergencyService.getHistory();
      }
    } catch (e) {
      debugPrint('Error loading emergency history: $e');
    } finally {
      isLoading = false;
      notifyListeners();
    }
  }
}
