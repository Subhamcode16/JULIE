use tauri::{Manager, PhysicalPosition};

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

      // Position the orb at the top-center of the primary monitor
      if let Some(window) = app.get_webview_window("main") {
        if let Ok(Some(monitor)) = window.current_monitor() {
          let screen_width = monitor.size().width;
          let orb_width: u32 = 100;
          let x = ((screen_width - orb_width) / 2) as i32;
          let y: i32 = 0; // Flush to the top edge
          let _ = window.set_position(PhysicalPosition::new(x, y));
        }
      }

      Ok(())
    })
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
