import re
import sys

def main():
    with open('tallermovil/lib/features/emergencies/views/detail/client/emergency_detail_view.dart', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the Cancelar Reparacion block (lines 2-63)
    lines = content.split('\n')
    cancelar_block = '\n'.join(lines[2:63])
    
    # The rest of the file starts after line 67 ("rt:io';")
    clean_lines = [lines[0], "import 'dart:io';"] + lines[68:]
    clean_content = '\n'.join(clean_lines)
    
    # Now we need to update the DefaultTabController
    clean_content = clean_content.replace('length: 2,', 'length: 3,')
    clean_content = clean_content.replace("tabs: [Tab(text: 'Detalle'), Tab(text: 'Cotizaciones')]", "tabs: [Tab(text: 'Detalle'), Tab(text: 'Cotizaciones'), Tab(text: 'Chat')]")
    
    # We need to extract the "Cotizaciones (Marketplace)" section.
    # It starts at: `            // Cotizaciones (Marketplace)`
    # It ends before: `            // Información del Vehículo`
    
    marketplace_start = clean_content.find('            // Cotizaciones (Marketplace)')
    marketplace_end = clean_content.find('            // Información del Vehículo')
    
    marketplace_block = clean_content[marketplace_start:marketplace_end]
    
    # Remove marketplace block from TAB 1
    clean_content = clean_content[:marketplace_start] + clean_content[marketplace_end:]
    
    # Now build TAB 2 content
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

    # Now find the end of TAB 1.
    # TAB 1 ends right before `      floatingActionButton:`
    tab1_end_pattern = r'( +)\],\n( +)\),\n( +)\),\n( +)floatingActionButton: FloatingActionButton.extended\('
    match = re.search(tab1_end_pattern, clean_content)
    if not match:
        print("Could not find end of TAB 1")
        # Let's try another pattern
        tab1_end_pattern2 = r'            TSpacing\.verticalXLarge\(\),\n          \],\n        \),\n      \),\n      floatingActionButton:'
        match2 = re.search(tab1_end_pattern2, clean_content)
        if match2:
            print("Found end of TAB 1 with pattern 2")
            idx = match2.end() - len('      floatingActionButton:')
            
            # Remove the floatingActionButton completely
            fab_end = clean_content.find('    );\n  }', idx)
            fab_end = clean_content.find(';', fab_end) + 1
            
            clean_content = clean_content[:idx] + tab2_content + """
        // TAB 3: CHAT
        ChatView(emergenciaId: e['id'], showAppBar: false),
      ],
    ),
  );
}
""" + clean_content[fab_end:]
            print("Successfully refactored")
            with open('tallermovil/lib/features/emergencies/views/detail/client/emergency_detail_view.dart', 'w', encoding='utf-8') as out:
                out.write(clean_content)
        else:
            print("Pattern 2 also failed.")
    
    # Fix the missing parenthesis in RatingSection at the end of the file
    clean_content = clean_content.replace('      onPressed: _openRating,\n  }\n}', '      onPressed: _openRating,\n    );\n  }\n}')
    with open('tallermovil/lib/features/emergencies/views/detail/client/emergency_detail_view.dart', 'w', encoding='utf-8') as out:
        out.write(clean_content)


if __name__ == '__main__':
    main()
