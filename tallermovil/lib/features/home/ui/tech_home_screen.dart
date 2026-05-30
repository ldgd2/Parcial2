import 'package:flutter/material.dart';

class TechHomeScreen extends StatelessWidget {
  const TechHomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Panel del Técnico',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  const Icon(Icons.build_circle, size: 64, color: Colors.blueAccent),
                  const SizedBox(height: 16),
                  const Text(
                    'No hay emergencias asignadas en este momento.',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 16, color: Colors.grey),
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton.icon(
                    onPressed: () {
                      // TODO: Recargar emergencias asignadas
                    },
                    icon: const Icon(Icons.refresh),
                    label: const Text('Actualizar panel'),
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 50),
                    ),
                  )
                ],
              ),
            ),
          )
        ],
      ),
    );
  }
}
