import serial
import serial.tools.list_ports
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib.widgets import Button, RadioButtons, TextBox
import os
import json
import matplotlib.image as mpimg
import filter_algo  # Force PyInstaller to scan and package this encrypted module
from pose_algo import PoseAlgorithm
import time

# --- Configure Matplotlib global font to prevent garbled characters ---
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun'] # Prioritize using Microsoft YaHei, SimHei, or SimSun
plt.rcParams['axes.unicode_minus'] = False # Display negative signs normally

# --- Serial Port Configuration ---
SERIAL_PORT = 'COM5' 
BAUD_RATE = 115200

# --- Global Interactive Log Cache ---
log_messages = []
MAX_LOG_LINES = 4
log_text_obj = None

def log_msg(msg):
    """Unified log output interface, synchronizing terminal printing and UI updates"""
    print(msg)
    t_str = time.strftime("%H:%M:%S")
    log_messages.append(f"[{t_str}] {msg}")
    if len(log_messages) > MAX_LOG_LINES:
        log_messages.pop(0)
    if log_text_obj is not None:
        log_text_obj.set_text("\n".join(log_messages))
        try: log_text_obj.figure.canvas.draw_idle()
        except: pass

# --- Configuration File Loading (for external modification of UI text and Logo) ---
CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    "languages": ["English", "中文"],
    "current_language": "English",
    "logo_path": "assets/logo.png",
    "中文": {
        "window_title": "3D 姿态监控系统",
        "plot_title": "三维避雷针姿态监控 - 专业版 v1",
        "btn_reset_text": "恢复物理真实坐标",
        "btn_cal_text": "当前位置重新置零",
        "log_conn_succ": "成功连接至物理端口: {port}",
        "log_conn_fail": "串口连接失败，自动转为纯模拟模式",
        "log_logo_fail": "警告: 无法加载企业 Logo 图片",
        "log_reset": ">>> 操作成功: 已恢复物理绝对重力坐标",
        "log_cal": ">>> 操作成功: 当前姿态已强行设为 0° 基准面",
        "log_sim_mode": ">>> 已切换至纯模拟数据模式",
        "log_reconn": ">>> 已尝试重新连接至: {port}",
        "log_sim_auto": ">>> 触发模拟操作，已自动切为模拟模式",
        "log_sim_apply": ">>> 模拟下发: Pitch={y} Roll={x} Acc={g} Temp={t}",
        "log_sim_err": ">>> [错误] 输入格式无效，请填写合法数字！",
        "log_key_sim": ">>> [快捷键] 自动应用模拟数据 (Apply Sim)",
        "log_key_cal": ">>> [快捷键] 自动执行置零校准 (Set Zero)"
    },
    "English": {
        "window_title": "3D Attitude Monitoring System",
        "plot_title": "3D Lightning Rod Monitor - Pro v1",
        "btn_reset_text": "Reset Original",
        "btn_cal_text": "Recalibrate (Set Zero)",
        "log_conn_succ": "Successfully connected to port: {port}",
        "log_conn_fail": "Serial connection failed, auto-switched to Simulation mode",
        "log_logo_fail": "Warning: Failed to load enterprise Logo image",
        "log_reset": ">>> Success: Restored absolute physical gravity coordinates",
        "log_cal": ">>> Success: Current attitude forcibly set as 0° reference plane",
        "log_sim_mode": ">>> Switched to pure simulation data mode",
        "log_reconn": ">>> Attempted to reconnect to: {port}",
        "log_sim_auto": ">>> Simulation triggered, auto-switched to Simulation mode",
        "log_sim_apply": ">>> Sim Applied: Pitch={y} Roll={x} Acc={g} Temp={t}",
        "log_sim_err": ">>> [Error] Invalid format, please enter valid numbers!",
        "log_key_sim": ">>> [Shortcut] Auto-applied simulation data (Apply Sim)",
        "log_key_cal": ">>> [Shortcut] Auto-executed zero calibration (Set Zero)"
    }
}

def load_config():
    need_rewrite = False
    if not os.path.exists(CONFIG_FILE):
        cfg = DEFAULT_CONFIG.copy()
        need_rewrite = True
    else:
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            if "languages" not in cfg: # Compatibility with older versions, force overwrite with new structure
                cfg = DEFAULT_CONFIG.copy()
                need_rewrite = True
        except:
            cfg = DEFAULT_CONFIG.copy()
            need_rewrite = True
            
    if need_rewrite:
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=4, ensure_ascii=False)
        except: pass
    return cfg

def save_config(cfg):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except Exception as e:
        log_msg(f"Failed to save config: {e}")

app_config = load_config()
current_lang = app_config.get("current_language", "English")

def get_lang_text(key, **kwargs):
    """Safely get the translated text for the current language"""
    text = app_config.get(current_lang, {}).get(key)
    if not text:
        text = DEFAULT_CONFIG.get(current_lang, {}).get(key, "")
    return text.format(**kwargs) if kwargs else text

ser = None
current_mode = 'Simulation'

def connect_serial(port):
    global ser, current_mode
    if ser and ser.is_open:
        ser.close()
        
    if port == 'Simulation':
        ser = None
        current_mode = 'Simulation'
        return True
        
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=0.001) 
        log_msg(get_lang_text("log_conn_succ", port=port))
        current_mode = port
        return True
    except Exception as e:
        log_msg(get_lang_text("log_conn_fail"))
        ser = None
        current_mode = 'Simulation'
        return False

# Attempt to connect to the default port on startup
connect_serial(SERIAL_PORT)

# --- Instantiate the core pose algorithm ---
pose_algo = PoseAlgorithm()

fig = plt.figure(figsize=(10, 8))
fig.canvas.manager.set_window_title(app_config[current_lang]["window_title"]) # Set the window title in the computer's taskbar/title bar

# --- Try to load an external Logo icon and display it in the bottom right corner ---
if app_config["logo_path"] and os.path.exists(app_config["logo_path"]):
    try:
        logo_img = mpimg.imread(app_config["logo_path"])
        # Create a separate area in the bottom right of the chart to display the Logo (absolute position, does not rotate with 3D plot)
        ax_logo = fig.add_axes([0.8, 0.05, 0.15, 0.15], zorder=1)
        ax_logo.imshow(logo_img, alpha=0.8) # alpha controls transparency
        ax_logo.axis('off') # Hide the logo's border and axes
    except Exception as e:
        log_msg(get_lang_text("log_logo_fail"))

ax = fig.add_subplot(111, projection='3d')
# Make space for the left panel and bottom log console
plt.subplots_adjust(left=0.25, bottom=0.26) 

# --- Button Function: Reset to Original (no calibration) ---
def reset_to_original(event):
    pose_algo.reset_offset()
    log_msg(get_lang_text("log_reset"))

# --- Button Function: Recalibrate (set current as 0 point) ---
def calibrate_to_current(event):
    pose_algo.calibrate_offset()
    log_msg(get_lang_text("log_cal"))

# --- UI Layout ---
ax_res = plt.axes([0.25, 0.05, 0.22, 0.075]) # Position for the reset original button
ax_cal = plt.axes([0.50, 0.05, 0.22, 0.075]) # Position for the recalibrate button

# --- Cool Interactive Log Terminal (CMD) ---
ax_log = plt.axes([0.25, 0.14, 0.53, 0.10], facecolor='black')
ax_log.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
for spine in ax_log.spines.values():
    spine.set_edgecolor('#333333') # Add a subtle dark gray border to the black box
log_text_obj = ax_log.text(0.02, 0.90, "\n".join(log_messages), color='white', fontsize=9, verticalalignment='top')

btn_reset = Button(ax_res, app_config[current_lang]["btn_reset_text"], color='#ff9999', hovercolor='#ff6666')
btn_cal = Button(ax_cal, app_config[current_lang]["btn_cal_text"], color='#99ff99', hovercolor='#66ff66')

btn_reset.on_clicked(reset_to_original)
btn_cal.on_clicked(calibrate_to_current)

# --- Left Panel: Language Switch Function ---
ax_lang = plt.axes([0.02, 0.88, 0.18, 0.08], facecolor='lightgoldenrodyellow')
ax_lang.set_title('Language', fontsize=10)

try:
    active_lang_idx = app_config["languages"].index(current_lang)
except ValueError:
    active_lang_idx = 0

lang_radio = RadioButtons(ax_lang, app_config["languages"], active=active_lang_idx)

def on_lang_select(label):
    global current_lang
    current_lang = label
    app_config["current_language"] = label
    save_config(app_config)
    
    # Dynamically update static UI elements
    fig.canvas.manager.set_window_title(app_config[label]["window_title"])
    btn_reset.label.set_text(app_config[label]["btn_reset_text"])
    btn_cal.label.set_text(app_config[label]["btn_cal_text"])
    log_msg(f">>> Language switched to: {label}")
    fig.canvas.draw_idle()
    
lang_radio.on_clicked(on_lang_select)

# --- Left Panel: Port Scanning and Simulation Data Function ---
ax_radio = plt.axes([0.02, 0.65, 0.18, 0.20], facecolor='lightgoldenrodyellow')
ax_btn_prev = plt.axes([0.02, 0.59, 0.08, 0.04])
ax_btn_next = plt.axes([0.12, 0.59, 0.08, 0.04])
ax_rescan = plt.axes([0.02, 0.54, 0.18, 0.04])

btn_prev = Button(ax_btn_prev, '< Prev')
btn_next = Button(ax_btn_next, 'Next >')
btn_rescan = Button(ax_rescan, 'Rescan Ports', color='lightblue')

available_ports = ['Simulation']
current_page = 0
PORTS_PER_PAGE = 4
radio_btn = None

def render_radio_buttons():
    global radio_btn, current_page, current_mode
    ax_radio.clear()
    
    start_idx = current_page * PORTS_PER_PAGE
    end_idx = start_idx + PORTS_PER_PAGE
    current_slice = available_ports[start_idx:end_idx]
    
    active_idx = 0
    if current_mode in current_slice:
        active_idx = current_slice.index(current_mode)
        
    total_pages = max(1, (len(available_ports) - 1) // PORTS_PER_PAGE + 1)
    ax_radio.set_title(f'Ports ({current_page+1}/{total_pages})')
    
    if not current_slice:
        plt.draw()
        return
        
    radio_btn = RadioButtons(ax_radio, current_slice, active=active_idx)
    
    def on_mode_select(label):
        if label == 'Simulation':
            connect_serial('Simulation')
            log_msg(get_lang_text("log_sim_mode"))
        else:
            if connect_serial(label):
                log_msg(get_lang_text("log_reconn", port=label))
            else:
                refresh_ports()
                
    radio_btn.on_clicked(on_mode_select)
    plt.draw()

def refresh_ports(event=None):
    global available_ports, current_page
    ports = [p.device for p in serial.tools.list_ports.comports()]
    available_ports = ports + ['Simulation']
    if current_mode in available_ports:
        current_page = available_ports.index(current_mode) // PORTS_PER_PAGE
    else:
        current_page = 0
    render_radio_buttons()

def prev_page(event):
    global current_page
    if current_page > 0:
        current_page -= 1
        render_radio_buttons()

def next_page(event):
    global current_page
    total_pages = (len(available_ports) - 1) // PORTS_PER_PAGE + 1
    if current_page < total_pages - 1:
        current_page += 1
        render_radio_buttons()

btn_prev.on_clicked(prev_page)
btn_next.on_clicked(next_page)
btn_rescan.on_clicked(refresh_ports)

# Load the list on initialization
refresh_ports()

# Simulation data input boxes
ax_box_x = plt.axes([0.1, 0.46, 0.08, 0.04])
ax_box_y = plt.axes([0.1, 0.39, 0.08, 0.04])
ax_box_g = plt.axes([0.1, 0.32, 0.08, 0.04])
ax_box_t = plt.axes([0.1, 0.25, 0.08, 0.04])

txt_x = TextBox(ax_box_x, 'Roll (X): ', initial='0.0')
txt_y = TextBox(ax_box_y, 'Pitch (Y): ', initial='0.0')
txt_g = TextBox(ax_box_g, 'Acc (G): ', initial='1.0')
txt_t = TextBox(ax_box_t, 'Temp (C): ', initial='25.0')

ax_btn_apply = plt.axes([0.02, 0.17, 0.08, 0.05])
ax_btn_reset_sim = plt.axes([0.12, 0.17, 0.08, 0.05])
btn_apply = Button(ax_btn_apply, 'Apply Sim', color='lightgreen')
btn_reset_sim = Button(ax_btn_reset_sim, 'Reset Sim', color='salmon')

# Simulation data cache [ID, Pitch, Roll, Acc, Temp]
sim_data_to_feed = [0.0, 0.0, 0.0, 1.0, 175.0] 

def apply_sim_data(event):
    global sim_data_to_feed
    try:
        x_val, y_val = float(txt_x.text), float(txt_y.text)
        g_val, t_val = float(txt_g.text), float(txt_t.text)
        # Add 150 to temperature (because internally the algorithm is raw_temp = raw_data[4] - 150)
        sim_data_to_feed = [0.0, y_val, x_val, g_val, t_val + 150.0]
        
        # Force switch to simulation mode to ensure the sent data takes effect immediately
        if current_mode != 'Simulation':
            connect_serial('Simulation')
            refresh_ports()
            log_msg(get_lang_text("log_sim_auto"))
            
        log_msg(get_lang_text("log_sim_apply", y=y_val, x=x_val, g=g_val, t=t_val))
    except ValueError:
        log_msg(get_lang_text("log_sim_err"))

def reset_sim_data(event):
    for txt in [txt_x, txt_y, txt_g, txt_t]:
        txt.set_val('0.0')
    apply_sim_data(None)

btn_apply.on_clicked(apply_sim_data)
btn_reset_sim.on_clicked(reset_sim_data)

def clear_selection(txt):
    """Clear the 'select all' state for the simulation textbox"""
    if getattr(txt, '_is_selected', False):
        txt.color = '1.0'        # Restore matplotlib default background color
        txt.hovercolor = '0.95'  # Restore matplotlib default hover color
        txt.ax.set_facecolor('white') # Restore white background
        txt.text_disp.set_color('black') # Restore black text
        txt._is_selected = False

def set_selection(txt):
    """Set and lock the 'select all' state with a dark blue background"""
    txt.color = '#0078D7'       # Force modify the default background color to prevent fading on mouse out
    txt.hovercolor = '#0078D7'  # Force modify the hover color to prevent color change on slight mouse movement
    txt.ax.set_facecolor('#0078D7') # Genuine Windows 'select all' dark blue background
    txt.text_disp.set_color('white') # Invert text color to white
    txt._is_selected = True

last_input_time = 0.0

def on_key_press_for_textbox(event):
    global last_input_time
    
    # --- Time logic for listening to the global Enter key ---
    if event.key == 'enter':
        if time.time() - last_input_time <= 3.0:
            log_msg(get_lang_text("log_key_sim"))
            apply_sim_data(None)
        else:
            log_msg(get_lang_text("log_key_cal"))
            calibrate_to_current(None)
        return
        
    for txt in [txt_x, txt_y, txt_g, txt_t]:
        if getattr(txt, 'capturekeystrokes', False):
            # If a valid typing modification occurs in the input box, refresh the last input time
            if event.key == 'backspace' or (event.key and len(event.key) == 1):
                last_input_time = time.time()
                
            if event.key == 'ctrl+a':
                set_selection(txt)
                fig.canvas.draw_idle()
            elif getattr(txt, '_is_selected', False):
                if event.key == 'backspace':
                    clear_selection(txt)
                    txt.set_val('')
                elif event.key and len(event.key) == 1:
                    clear_selection(txt)
                    txt.set_val(event.key) # Instantly overwrite the selected content when typing a new character
                elif event.key in ['left', 'right', 'up', 'down', 'home', 'end']:
                    clear_selection(txt)
                    fig.canvas.draw_idle()

def on_mouse_press_for_textbox(event):
    for txt in [txt_x, txt_y, txt_g, txt_t]:
        if event.dblclick and event.inaxes == txt.ax:
            set_selection(txt)
            fig.canvas.draw_idle()
        else:
            if getattr(txt, '_is_selected', False):
                clear_selection(txt)
                fig.canvas.draw_idle()

fig.canvas.mpl_connect('key_press_event', on_key_press_for_textbox)
fig.canvas.mpl_connect('button_press_event', on_mouse_press_for_textbox)

def update(frame):
    global current_mode, sim_data_to_feed
    raw_data = None
    
    if current_mode == 'Simulation':
        raw_data = sim_data_to_feed
    else:
        line = None
        if ser and ser.is_open:
            try:
                while ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
            except Exception:
                pass # Ignore read exceptions caused by hot-plugging
        
        if line:
            try:
                parsed = [float(x) for x in line.split(',')]
                if len(parsed) >= 3:
                    raw_data = parsed
            except:
                pass
                
    if raw_data is not None and len(raw_data) >= 3:
        # --- Delegate data processing and conversion to the core algorithm class ---
        is_sim = (current_mode == 'Simulation')
        pitch_disp, roll_disp, acc, temp, x_pos, y_pos, z_pos = pose_algo.process_raw_data(raw_data, bypass_filter=is_sim)

# --- Modified Plotting Settings ---
        ax.clear()
        # Adjust view angle: elev is elevation, azim is azimuth. elev=25, azim=-45 gives the best visual
        ax.view_init(elev=25, azim=-45) 
        
        ax.set_xlim([-1, 1]); ax.set_ylim([-1, 1]); ax.set_zlim([0, 1.1])
        ax.set_xlabel('Roll (X)'); ax.set_ylabel('Pitch (Y)')
        
        # Drawing logic remains unchanged...
        ax.plot([0, x_pos], [0, y_pos], [0, z_pos], color='#1f77b4', lw=6, marker='o', ms=10)
        ax.plot([x_pos, x_pos], [y_pos, y_pos], [0, z_pos], 'r:', alpha=0.5)
        
        # --- Key: Move the text box position ---
        # Change the first parameter from 0.05 to 0.02 (move a bit to the left)
        # Change the second parameter from 0.95 to 0.85 (move down a bit to avoid the title)
        mode_str = "RELATIVE" if pose_algo.is_relative() else "ORIGINAL"
        info = (f"MODE: {mode_str}\n"
                f"Pitch (Y): {pitch_disp:.2f}°\n"
                f"Roll (X): {roll_disp:.2f}°\n"
                f"Acc: {acc:.2f}G | Temp: {temp:.1f}℃")
        
        # Using transform=fig.transFigure keeps the text fixed in the upper left corner of the window, unaffected by 3D graph rotation
        # --- Precisely position the text box above the left buttons (red box area) ---
        mode_str = "RELATIVE" if pose_algo.is_relative() else "ORIGINAL"
        info = (f"STATUS: {mode_str}\n"
                f"Pitch (Y): {pitch_disp:.2f}°\n"
                f"Roll (X): {roll_disp:.2f}°\n"
                f"Total Acc: {acc:.2f}G\n"
                f"Temp: {temp:.1f}℃")
        
        # Use fig.transFigure for absolute coordinates
        # x=0.12 to align with the center of the Reset button
        # y=0.20 to float just above the buttons without obscuring the axes
# --- Precisely align with the "HERE" red box position in the top left ---
        mode_str = "RELATIVE" if pose_algo.is_relative() else "ORIGINAL"
        info = (f"STATUS: {mode_str}\n"
                f"Pitch (Y): {pitch_disp:.2f}°\n"
                f"Roll (X): {roll_disp:.2f}°\n"
                f"Total Acc: {acc:.2f}G\n"
                f"Temp: {temp:.1f}℃")
        
        # x=0.25: Move right to avoid the new left control panel
        # y=0.80: Raise significantly to align with the red box height
        # transform=fig.transFigure: Ensures the text box is fixed at this position in the window and does not rotate with the 3D plot
        ax.text2D(0.25, 0.85, info, transform=fig.transFigure, fontsize=11, 
                  verticalalignment='top', horizontalalignment='left',
                  bbox=dict(facecolor='white', alpha=0.8, edgecolor='navy', boxstyle='round,pad=0.5'))
        
        # Adjust the title to leave visual space for the red box
        lang = app_config.get("current_language", "English")
        ax.set_title(app_config[lang]["plot_title"], pad=20)

# Set interval to 20ms, combined with the while loop reading, to achieve a zero-latency feel
ani = animation.FuncAnimation(fig, update, interval=20, cache_frame_data=False)
plt.show()
if ser and ser.is_open:
    ser.close()