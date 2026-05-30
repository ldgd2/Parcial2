import 'package:flutter/material.dart';
import '../../../../core/storage/local_storage.dart';
import '../../emergencies/views/history/emergency_history_view.dart';
import '../../emergencies/views/report_emergency/report_emergency_view.dart';
import '../../vehicles/ui/vehicle_settings_screen.dart';
import '../../settings/ui/settings_screen.dart';
import 'home_screen.dart';
import 'tech_home_screen.dart';

class MainNavigationScreen extends StatefulWidget {
  const MainNavigationScreen({super.key});

  @override
  State<MainNavigationScreen> createState() => _MainNavigationScreenState();
}

class _MainNavigationScreenState extends State<MainNavigationScreen> {
  int _currentIndex = 0;
  bool _isLoading = true;
  String _role = 'cliente';

  @override
  void initState() {
    super.initState();
    _loadRole();
  }

  Future<void> _loadRole() async {
    final rol = await LocalStorage().getRol();
    setState(() {
      _role = rol ?? 'cliente';
      _isLoading = false;
    });
  }

  List<Widget> get _screens {
    if (_role == 'tecnico') {
      return [
        const TechHomeScreen(),
        const EmergencyHistoryView(),
        const SettingsScreen(),
      ];
    }
    return [
      const HomeScreen(),
      const VehicleSettingsScreen(),
      const EmergencyHistoryView(),
      const SettingsScreen(),
    ];
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    final isTecnico = _role == 'tecnico';

    return Scaffold(
      appBar: AppBar(
        title: Image.asset('assets/logo_small.png', height: 30, errorBuilder: (_, __, ___) => Text(isTecnico ? 'Panel Técnico' : 'Taller OS')),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () {
              setState(() => _currentIndex = isTecnico ? 2 : 3); // Ir a Ajustes
            },
          ),
        ],
      ),
      body: _screens[_currentIndex],
      floatingActionButton: isTecnico ? null : FloatingActionButton(
        onPressed: () {
          Navigator.push(context, MaterialPageRoute(builder: (_) => const ReportEmergencyView()));
        },
        backgroundColor: Colors.redAccent,
        elevation: 8,
        tooltip: 'Reportar Emergencia S.O.S',
        child: const Icon(Icons.sos, color: Colors.white, size: 32),
      ),
      floatingActionButtonLocation: isTecnico ? null : FloatingActionButtonLocation.centerDocked,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        items: isTecnico ? const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Inicio',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history_outlined),
            activeIcon: Icon(Icons.history),
            label: 'Actividad',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Ajustes',
          ),
        ] : const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Inicio',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions_car_outlined),
            activeIcon: Icon(Icons.directions_car),
            label: 'Vehículos',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history_outlined),
            activeIcon: Icon(Icons.history),
            label: 'Actividad',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Ajustes',
          ),
        ],
      ),
    );
  }
}
