import re
import sys

def main():
    with open('tallermovil/lib/features/emergencies/views/detail/client/emergency_detail_view.dart', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # 1. Extract Cancelar Reparacion block (lines 2..62)
    cancelar_block = '\n'.join(lines[2:63])
    
    # 2. Fix the file header
    clean_lines = [lines[0], "import 'dart:io';"] + lines[68:]
    text = '\n'.join(clean_lines)
    
    # 3. Update tabs length
    text = text.replace('DefaultTabController(\n      length: 2,', 'DefaultTabController(\n      length: 3,')
    text = text.replace("tabs: [Tab(text: 'Detalle'), Tab(text: 'Cotizaciones')]", "tabs: [Tab(text: 'Detalle'), Tab(text: 'Cotizaciones'), Tab(text: 'Chat')]")
    
    # 4. Extract marketplace block from TAB 1
    # Find `            // Cotizaciones (Marketplace)`
    marketplace_start = text.find('            // Cotizaciones (Marketplace)')
    marketplace_end = text.find('            // Información del Vehículo')
    if marketplace_start == -1 or marketplace_end == -1:
        print("Could not find marketplace block")
        sys.exit(1)
        
    marketplace_block = text[marketplace_start:marketplace_end]
    
    # Remove marketplace block from TAB 1
    text = text[:marketplace_start] + text[marketplace_end:]
    
    # 5. Build TAB 2
    tab2_content = """        // TAB 2: COTIZACIONES
        SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
""" + cancelar_block + "\n" + marketplace_block + """            ],
          ),
        ),
"""
    
    # 6. Insert TAB 2 and TAB 3 at the end of TabBarView, and remove FAB
    # Find the end of TAB 1 in TabBarView:
    # `            TSpacing.verticalXLarge(),\n          ],\n        ),\n      ),`
    end_of_tab1 = text.find('            TSpacing.verticalXLarge(),\n          ],\n        ),\n      ),')
    if end_of_tab1 == -1:
        print("Could not find end of TAB 1")
        sys.exit(1)
        
    insertion_point = end_of_tab1 + len('            TSpacing.verticalXLarge(),\n          ],\n        ),\n      ),')
    
    # Find the FAB
    fab_start = text.find('      floatingActionButton: FloatingActionButton.extended(')
    fab_end = text.find('      ),', fab_start)
    fab_end = text.find('    );\n  }', fab_end)
    fab_end = text.find(';', fab_end) + 1
    
    if fab_start == -1 or fab_end == -1:
        print("Could not find FAB")
        sys.exit(1)
        
    text = text[:insertion_point] + "\n" + tab2_content + """        // TAB 3: CHAT
        ChatView(emergenciaId: e['id'], showAppBar: false),
      ],
    ),
  );
}""" + text[fab_end:]
    
    # 7. Fix RatingSection
    text = text.replace('      onPressed: _openRating,\n  }\n}', '      onPressed: _openRating,\n    );\n  }\n}')
    
    with open('tallermovil/lib/features/emergencies/views/detail/client/emergency_detail_view.dart', 'w', encoding='utf-8') as f:
        f.write(text)
    
    print("Refactoring complete.")

if __name__ == '__main__':
    main()
