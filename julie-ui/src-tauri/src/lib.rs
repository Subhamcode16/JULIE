use tauri::{Manager, PhysicalPosition};

// No more manual Win32 Z-order hacks!

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
  tauri::Builder::default()
    .setup(|app| {
      if cfg!(debug_assertions) {
        app.handle().plugin(
          tauri_plugin_log::Builder::default()
            .level(log::LevelFilter::Info)
            .build(),
        )?;
      }

      if let Some(window) = app.get_webview_window("main") {
        // We will no longer set_ignore_cursor_events(true) on the main window if it needs dragging
        // Center it perfectly at the TOP of the screen using Tauri's native math
        if let Ok(Some(monitor)) = window.current_monitor() {
            let monitor_pos = monitor.position(); // Physical Position
            let monitor_size = monitor.size(); // Physical Size
            if let Ok(window_size) = window.outer_size() {
                let x = monitor_pos.x + ((monitor_size.width as i32 - window_size.width as i32) / 2);
                let y = monitor_pos.y; // Top of the monitor
                let _ = window.set_position(PhysicalPosition::new(x, y));
            }
        }
      }

      if let Some(cursor_window) = app.get_webview_window("ai-cursor") {
        let _ = cursor_window.set_ignore_cursor_events(true);
      }

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
