import os
import shutil
import glob

base = 'tallermovil/lib/features'

moves = {
    # Home
    f'{base}/home/ui/home_screen.dart': f'{base}/home/ui/client/home_screen.dart',
    f'{base}/home/ui/home_controller.dart': f'{base}/home/ui/client/home_controller.dart',
    f'{base}/home/ui/tech_home_screen.dart': f'{base}/home/ui/tech/tech_home_screen.dart',
    f'{base}/home/ui/tech_activity_screen.dart': f'{base}/home/ui/tech/tech_activity_screen.dart',
    
    # Emergencies Detail
    f'{base}/emergencies/views/detail/emergency_detail_view.dart': f'{base}/emergencies/views/detail/client/emergency_detail_view.dart',
    f'{base}/emergencies/views/detail/quote_review_view.dart': f'{base}/emergencies/views/detail/client/quote_review_view.dart',
    f'{base}/emergencies/views/detail/rating_dialog.dart': f'{base}/emergencies/views/detail/client/rating_dialog.dart',
    f'{base}/emergencies/views/detail/payment_simulator_view.dart': f'{base}/emergencies/views/detail/client/payment_simulator_view.dart',
    
    f'{base}/emergencies/views/detail/tech_emergency_detail_view.dart': f'{base}/emergencies/views/detail/tech/tech_emergency_detail_view.dart',
    f'{base}/emergencies/views/detail/live_tracking_screen.dart': f'{base}/emergencies/views/detail/tech/live_tracking_screen.dart',
    f'{base}/emergencies/views/detail/adjust_quote_dialog.dart': f'{base}/emergencies/views/detail/tech/adjust_quote_dialog.dart',
    f'{base}/emergencies/views/detail/widgets/tech_quote_adjustment_dialog.dart': f'{base}/emergencies/views/detail/tech/widgets/tech_quote_adjustment_dialog.dart',
}

# Create dirs
for dest in moves.values():
    os.makedirs(os.path.dirname(dest), exist_ok=True)

# Move files
for src, dest in moves.items():
    if os.path.exists(src):
        shutil.move(src, dest)
        print(f'Moved {src} -> {dest}')
    else:
        print(f'Warning: {src} not found.')

print('Done moving files.')
