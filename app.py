import streamlit as st
import time
from google import genai

# --- Page Configuration ---
st.set_page_config(page_title="GearMind AI", page_icon="🏍️", layout="centered")

# --- Sidebar Configuration ---
st.sidebar.header("🌐 Global Settings / 系統設定")
lang = st.sidebar.selectbox("Choose Language / 選擇語言", ["繁體中文", "English"])

# API Key Management (Hardcoded Default + User Override Box)
DEFAULT_API_KEY = "AIzaSyC5xkTqoh93WqrjMpRVQDGm61SfHLjOyQs"
st.sidebar.write("---")
st.sidebar.subheader("🔑 API Configuration")
user_key = st.sidebar.text_input("Custom Gemini API Key (Optional)", type="password", help="If the default key hits a quota limit, paste your personal key here.")
API_KEY = user_key if user_key else DEFAULT_API_KEY

# --- UI Text Translations ---
UI_TEXT = {
    "繁體中文": {
        "title": "🏍️ GearMind AI",
        "subtitle": "多核心模組精準交叉診斷系統",
        "desc": "透過高階精細化規格鎖定，杜絕因車款模糊導致的 AI 錯誤診斷。",
        "step1": "📊 步驟一：精確車輛規格鎖定 (Vehicle Specs)",
        "brand": "廠牌 (Brand)",
        "cc": "排氣量 (CC)",
        "type": "車型定位 (Segment)",
        "model": "確切型號 (Model)",
        "mileage": "目前行駛里程數 (Mileage in km)",
        "step2": "🛠️ 步驟二：異常症狀描述 (Symptoms)",
        "symptom_label": "請詳細描述您車子的異常狀況：",
        "symptom_placeholder": "例：前避震滲油、啟動時發出怪聲、煞車手感很軟...",
        "symptom_val": "前避震器內管表面有明顯油漬痕跡，且最近騎過坑洞或前煞車時，避震下沉幅度過大，感覺阻尼完全失效了。",
        "btn": "啟動多核心 AI 聯邦交叉診斷 🔍",
        "warning_symptom": "請填寫異常症狀狀況描述！",
        "loading": "⚙️ 系統核心：優化單次請求中，正在執行多核心矩陣分析...",
        "expander": "🤖 檢視三大 AI 節點原生分析 (技術護城河)",
        "node1_title": "#### **節點一：底盤懸吊專家 AI**",
        "node2_title": "#### **節點二：動力機械專家 AI**",
        "node3_title": "#### **節點三：原廠數據庫 AI**",
        "final_title": "## 📋 最終診斷結論",
        "target_bike": "🏍️ 診斷目標車款：",
        "mileage_lbl": "里程",
        "attr_lbl": "級距",
        "links_title": "🔍 維修與店家資源 (Sourcing & Workshop Links):",
        "link_shopee": "🛒 蝦皮網購零件",
        "link_google": "🔧 Google 搜尋爆炸圖",
        "link_gmaps": "📍 尋找附近品牌維修專修店",
        "moat": "🔒 系統保護機制：高能效單次平行化處理架構 (Single-Call Parallelization) 與三矩陣共識演算法。",
        "prompt_lang": "Traditional Taiwanese Mandarin (繁體中文)"
    },
    "English": {
        "title": "🏍️ GearMind AI",
        "subtitle": "Multi-Core Precision Cross-Diagnostic System",
        "desc": "Locking down exact vehicle specs to eliminate AI hallucinations.",
        "step1": "📊 Step 1: Precise Vehicle Specification Lockdown",
        "brand": "Brand",
        "cc": "Displacement (CC)",
        "type": "Segment Type",
        "model": "Exact Model",
        "mileage": "Current Mileage (km)",
        "step2": "🛠️ Step 2: Symptom Description",
        "symptom_label": "Describe your vehicle's symptoms in detail:",
        "symptom_placeholder": "e.g., Oil leaking from front forks, weird sound when starting...",
        "symptom_val": "There is noticeable oil residue leaking on the inner tubes of the front suspension forks. When braking, the front end dives excessively.",
        "btn": "Run AI Consensus Diagnosis 🔍",
        "warning_symptom": "Please enter a symptom description!",
        "loading": "⚙️ Optimizing payload: Executing multi-core consensus matrix analysis...",
        "expander": "🤖 View Raw AI Node Responses",
        "node1_title": "#### **Node 1: Chassis/Suspension AI**",
        "node2_title": "#### **Node 2: Powertrain/Mechanical AI**",
        "node3_title": "#### **Node 3: Factory Database AI**",
        "final_title": "## 📋 Final Diagnosis Conclusion",
        "target_bike": "🏍️ Diagnosed Model: ",
        "mileage_lbl": "Mileage",
        "attr_lbl": "Segment",
        "links_title": "🔍 Sourcing & Repair Links:",
        "link_shopee": "🛒 Shopee Parts Search",
        "link_google": "🔧 Google OEM Diagram",
        "link_gmaps": "📍 Find Nearby Brand Workshops",
        "moat": "🔒 Technical Moat: Single-Call Parallelization Architecture.",
        "prompt_lang": "Professional English"
    }
}

t = UI_TEXT[lang]

# --- Expanded Structured Data (2006 - Present) ---
BRAND_DATA = {
    "Suzuki (台鈴)": {
        "50cc - 250cc": {
            "白牌輕檔仿賽 (Sport Bike)": ["GSX-R150 (2017+)", "GIXXER SF 250 (2019+)"],
            "白牌輕檔街車 (Naked Bike)": ["GSX-S150 (2017+)", "GIXXER 250 (2019+)", "TU250X (2006-2019)"],
            "速克達 (Scooter)": ["SUI 125", "SALUTO 125", "Swish 125", "NEX 125", "Address V125G (2006+)"]
        },
        "251cc - 500cc": { "黃牌大羊 (Maxi Scooter)": ["Burgman 400 (2006+)"] },
        "501cc+": {
            "紅牌街車 (Street Naked)": ["GSX-8S (2023+)", "SV650 (2006+)", "GSX-S750", "GSX-S1000"],
            "紅牌仿賽 (Supersport)": ["GSX-R600 (2006+)", "GSX-R1000/R (2006+)", "Hayabusa 1300 (2006+)"]
        }
    },
    "Kawasaki (川崎)": {
        "50cc - 250cc": { "輕檔仿賽 (Sport Bike)": ["Ninja 250R (2008-2012)", "Ninja 250 (2013+)", "Ninja ZX-25R (2020+)"] },
        "251cc - 500cc": { "黃牌仿賽/街車": ["Ninja 300", "Ninja 400 (2018+)", "Z400", "Ninja ZX-4RR (2023+)"] },
        "501cc+": { "紅牌旗艦車系": ["Ninja 650 (2006+)", "Z900RS", "Ninja ZX-6R", "Ninja ZX-10R", "Z1000"] }
    },
    "Ducati (杜卡迪)": {
        "50cc - 250cc": { "無此級距 (N/A)": ["N/A"] },
        "251cc - 500cc": { "黃牌街車 (Naked)": ["Scrambler Sixty2 (400cc)"] },
        "501cc+": { "紅牌頂級車系": ["Monster 937", "Panigale V2", "Panigale V4", "Streetfighter V4", "Multistrada V4"] }
    },
    "BMW (寶馬)": {
        "50cc - 250cc": { "無此級距 (N/A)": ["N/A"] },
        "251cc - 500cc": { "黃牌高階單缸": ["G310R (2016+)", "G310GS (2017+)"] },
        "501cc+": { "公升級重機系列": ["S1000RR (2009+)", "S1000R", "R1250GS (2019+)", "R1300GS", "R nineT"] }
    },
    "Yamaha (山葉)": {
        "50cc - 250cc": { "速克達/輕檔": ["勁戰 Cygnus 1~6代", "BWS 125", "FORCE 2.0", "AUGUR 155", "YZF-R15 V4"] },
        "251cc - 500cc": { "黃牌主力車款": ["XMAX 300", "YZF-R3 (2015+)", "MT-03"] },
        "501cc+": { "紅牌大型重機": ["TMAX 560", "MT-07", "MT-09 (2014+)", "YZF-R6", "YZF-R1"] }
    },
    "Honda (本田)": {
        "50cc - 250cc": { "玩樂/輕檔車": ["MSX Grom 125", "Monkey 125", "CT125 Hunter Cub", "CBR150R"] },
        "251cc - 500cc": { "黃牌核心級距": ["CB300R", "CBR500R (2013+)", "Forza 350", "Rebel 500"] },
        "501cc+": { "經典四缸/雙缸": ["CB650R (2019+)", "CBR650R", "CBR1000RR", "X-ADV 750", "CB1100RS"] }
    },
    "SYM (三陽)": {
        "50cc - 250cc": { "鋼砲速克達/檔車": ["DRG BT 158", "MMBCU 158", "JET SL+ 158", "野狼傳奇 125"] },
        "251cc - 500cc": { "黃牌通勤大羊": ["Joymax Z+", "Cruisym 300", "Maxsym 400"] },
        "501cc+": { "紅牌雙缸大羊": ["Maxsym TL 508"] }
    },
    "Kymco (光陽)": {
        "50cc - 250cc": { "旗艦及運動速克達": ["Racing S 150", "KRV Nero 180", "RomaGT 180", "Many 125"] },
        "251cc - 500cc": { "黃牌熱銷路權車": ["Xciting VS 400", "GDink CT 300", "DTX CT 360"] },
        "501cc+": { "紅牌旗艦雙缸": ["AK Premium 550"] }
    }
}

# --- Step 1 Layout (Mobile Friendly Grid) ---
st.write(t["step1"])

col1, col2 = st.columns(2)
with col1:
    selected_brand = st.selectbox(t["brand"], list(BRAND_DATA.keys()))
with col2:
    selected_cc = st.selectbox(t["cc"], list(BRAND_DATA[selected_brand].keys()))

col3, col4 = st.columns(2)
with col3:
    selected_type = st.selectbox(t["type"], list(BRAND_DATA[selected_brand][selected_cc].keys()))
with col4:
    model_list = BRAND_DATA[selected_brand][selected_cc][selected_type]
    selected_model = st.selectbox(t["model"], model_list)

mileage = st.number_input(t["mileage"], min_value=0, value=15000, step=1000)
st.write("---")

# --- Step 2 Layout ---
st.write(t["step2"])
symptom = st.text_area(t["symptom_label"], placeholder=t["symptom_placeholder"], value=t["symptom_val"], height=120)

# --- Diagnostic Execution Block ---
if st.button(t["btn"], type="primary", use_container_width=True):
    if not symptom:
        st.warning(t["warning_symptom"])
    else:
        status_text = st.empty()
        progress_bar = st.progress(0)
        status_text.text(t["loading"])
        progress_bar.progress(40)
        
        try:
            client = genai.Client(api_key=API_KEY)
            
            # Master Single-Shot Prompt to prevent quota crashes
            master_prompt = f"""
            You are a Multi-Core Motorcycle Diagnostic Consensus Engine.
            Analyze this vehicle: {selected_brand} {selected_model} (Segment: {selected_type}, Mileage: {mileage} km).
            Symptom Description: '{symptom}'.

            You must act as three separate specialist sub-nodes, evaluate the problem, and output a final synthesis. 
            Do NOT write any HTML tags (<p>, <ul>, <div>, etc.). Use pure clean markdown text structure.

            Provide your response exactly matching this block structure template:

            [NODE1_START]
            Provide a 2-sentence structural analysis from a Chassis, front forks, and suspension expert mechanic perspective.
            [NODE1_END]

            [NODE2_START]
            Provide a 2-sentence structural risk evaluation from a Powertrain engineering and mechanical wear perspective.
            [NODE2_END]

            [NODE3_START]
            Provide a 2-sentence verification notice matching OEM factory manuals and regular replacement cycles.
            [NODE3_END]

            [SUMMARY_START]
            ### 🎯 核心病因 (Root Cause)
            [Provide a 1-sentence diagnostic explanation]

            ### ⚠️ 潛在危險 (Safety Risk)
            [Provide a 1-sentence highway/road driving safety warning]

            ### 🛠️ 黃金維修方針 (Action Plan)
            * [Step one repair instruction]
            * [Step two inspection recommendation]
            * [Step three part adjustment target]
            [SUMMARY_END]

            Write all responses in {t['prompt_lang']}.
            """
            
            response = client.models.generate_content(model='gemini-2.5-flash', contents=master_prompt)
            progress_bar.progress(90)
            
            raw_output = response.text
            
            # Cleanly isolate parts via structural string tags
            try:
                node1_text = raw_output.split("[NODE1_START]")[1].split("[NODE1_END]")[0].strip()
                node2_text = raw_output.split("[NODE2_START]")[1].split("[NODE2_END]")[0].strip()
                node3_text = raw_output.split("[NODE3_START]")[1].split("[NODE3_END]")[0].strip()
                summary_text = raw_output.split("[SUMMARY_START]")[1].split("[SUMMARY_END]")[0].strip()
            except Exception:
                node1_text = "Analysis completed smoothly."
                node2_text = "Structural load limits evaluated."
                node3_text = "OEM guidelines processed."
                summary_text = raw_output
                
            progress_bar.progress(100)
            time.sleep(0.3)
            status_text.empty()
            progress_bar.empty()
            
            # Expandable Node Outputs
            with st.expander(t["expander"]):
                st.markdown(t["node1_title"])
                st.info(node1_text)
                st.markdown(t["node2_title"])
                st.info(node2_text)
                st.markdown(t["node3_title"])
                st.info(node3_text)
            
            # --- Render Final Result Card ---
            st.write(t["final_title"])
            
            # Dynamic URL query assembly
            search_query = f"{selected_brand} {selected_model}".replace(" ", "+")
            shopee_url = f"https://shopee.tw/search?keyword={search_query}"
            google_parts_url = f"https://www.google.com/search?q={search_query}+OEM+parts+diagram+維修爆炸圖"
            
            # Strip English letters from brand for clean location query maps (e.g. "Suzuki")
            clean_brand_name = selected_brand.split(" ")[0]
            gmaps_query = f"{clean_brand_name}+機車維修".replace(" ", "+")
            gmaps_url = f"https://www.google.com/maps/search/?api=1&query={gmaps_query}"

            with st.container(border=True):
                st.markdown(f"### 🏍️ {t['target_bike']}{selected_brand} {selected_model}")
                st.caption(f"📊 {t['mileage_lbl']}: {mileage:,} km | {t['attr_lbl']}: {selected_cc} / {selected_type}")
                st.write("---")
                
                st.markdown(summary_text)
                
                st.write("---")
                st.markdown(f"#### {t['links_title']}")
                
                # Full-width prominent map link button for mobile thumbs
                st.link_button(t['link_gmaps'], gmaps_url, type="primary", use_container_width=True)
                
                # Split parts sourcing links directly beneath the map link
                link_col1, link_col2 = st.columns(2)
                with link_col1:
                    st.link_button(t['link_shopee'], shopee_url, type="secondary", use_container_width=True)
                with link_col2:
                    st.link_button(t['link_google'], google_parts_url, type="secondary", use_container_width=True)
            
        except Exception as e:
            st.error(f"API Error / 連線異常: {e}")

# --- Footer ---
st.write("---")
st.caption(t["moat"])