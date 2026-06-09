import sys

def main():
    with open('tallermovil/lib/features/emergencies/views/detail/client/emergency_detail_view.dart', 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Fix Error 1: Marketplace block outside array
    bad_pattern = """                  TSpacing.verticalLarge(),
                ],

              ],
            ),
            // Cotizaciones (Marketplace)"""
    good_pattern = """                  TSpacing.verticalLarge(),
                ],

            // Cotizaciones (Marketplace)"""
    text = text.replace(bad_pattern, good_pattern)
    
    # We also need to add the closing array and column and singlechildscrollview at the end of TAB 2.
    # Where does TAB 2 end? It ends before `        // TAB 3: CHAT`.
    # Let's find it.
    end_tab2_pattern = """              TSpacing.verticalLarge(),
            ],
        // TAB 3: CHAT"""
    end_tab2_replacement = """              TSpacing.verticalLarge(),
            ],
          ],
        ),
      ),
        // TAB 3: CHAT"""
    text = text.replace(end_tab2_pattern, end_tab2_replacement)
    
    # Fix Error 2: Extra closing brace
    bad_brace = """      ],
    ),
  );
}
  }

  Widget _buildStatusBadge(String status) {"""
    good_brace = """      ],
    ),
  );
}

  Widget _buildStatusBadge(String status) {"""
    text = text.replace(bad_brace, good_brace)
    
    with open('tallermovil/lib/features/emergencies/views/detail/client/emergency_detail_view.dart', 'w', encoding='utf-8') as f:
        f.write(text)
    
    print("Fixed syntax errors.")

if __name__ == '__main__':
    main()
