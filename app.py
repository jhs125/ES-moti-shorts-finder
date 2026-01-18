import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import re

# ================== PAGE CONFIG ==================

st.set_page_config(
    page_title="Spanish Motivation Shorts Finder",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================== CUSTOM CSS ==================

st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #e63946 0%, #f4a261 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .viral-badge {
        background: #ff4757;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .success-badge {
        background: #2ed573;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
    }
    .spanish-header {
        background: linear-gradient(90deg, #c60b1e 0%, #c60b1e 25%, #ffc400 25%, #ffc400 75%, #c60b1e 75%, #c60b1e 100%);
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background-color: transparent;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ================== CONSTANTS ==================

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Spanish-speaking regions
REGION_CODES = {
    "🇪🇸 España (Spain)": "ES",
    "🇲🇽 México": "MX",
    "🇦🇷 Argentina": "AR",
    "🇨🇴 Colombia": "CO",
    "🇨🇱 Chile": "CL",
    "🇵🇪 Perú": "PE",
    "🇻🇪 Venezuela": "VE",
    "🇪🇨 Ecuador": "EC",
    "🇬🇹 Guatemala": "GT",
    "🇨🇺 Cuba": "CU",
    "🇧🇴 Bolivia": "BO",
    "🇩🇴 República Dominicana": "DO",
    "🇭🇳 Honduras": "HN",
    "🇵🇾 Paraguay": "PY",
    "🇸🇻 El Salvador": "SV",
    "🇳🇮 Nicaragua": "NI",
    "🇨🇷 Costa Rica": "CR",
    "🇵🇦 Panamá": "PA",
    "🇺🇾 Uruguay": "UY",
    "🇺🇸 USA (Hispanic)": "US",
}

# ================== SPANISH MOTIVATION KEYWORDS ==================

NICHE_KEYWORDS = {
    "💪 Motivación General": [
        "motivación español",
        "motivación personal",
        "frases motivacionales",
        "motivación diaria",
        "palabras de motivación",
        "motivación para la vida",
        "mensajes motivacionales",
        "reflexiones motivacionales",
        "motivación cortos",
        "motivación shorts",
    ],
    "🏆 Éxito y Superación": [
        "éxito personal",
        "superación personal",
        "cómo tener éxito",
        "mentalidad de éxito",
        "historias de éxito",
        "claves del éxito",
        "éxito en la vida",
        "secretos del éxito",
        "camino al éxito",
        "mentalidad ganadora",
    ],
    "💰 Dinero y Riqueza": [
        "motivación dinero",
        "mentalidad millonaria",
        "riqueza mentalidad",
        "libertad financiera",
        "éxito financiero",
        "cómo ser rico",
        "dinero y éxito",
        "abundancia financiera",
        "mentalidad de rico",
        "educación financiera motivación",
    ],
    "🧠 Mentalidad y Mindset": [
        "mentalidad positiva",
        "cambiar mentalidad",
        "mentalidad de crecimiento",
        "psicología del éxito",
        "mente millonaria",
        "reprogramar la mente",
        "mentalidad fuerte",
        "poder de la mente",
        "actitud mental positiva",
        "mentalidad emprendedora",
    ],
    "📈 Emprendimiento": [
        "motivación emprendedor",
        "emprendimiento shorts",
        "consejos emprendedores",
        "éxito emprendedor",
        "historias emprendedores",
        "mentalidad emprendedora",
        "cómo emprender",
        "negocios motivación",
        "emprender desde cero",
        "ser tu propio jefe",
    ],
    "⏰ Disciplina y Hábitos": [
        "disciplina personal",
        "hábitos exitosos",
        "rutina de éxito",
        "autodisciplina",
        "hábitos millonarios",
        "constancia y disciplina",
        "hábitos diarios éxito",
        "despertar temprano motivación",
        "productividad personal",
        "gestión del tiempo",
    ],
    "❤️ Amor Propio y Autoestima": [
        "amor propio",
        "autoestima alta",
        "quererse a uno mismo",
        "confianza en ti mismo",
        "valorarte a ti mismo",
        "aceptación personal",
        "empoderamiento personal",
        "creer en ti mismo",
        "fortaleza interior",
        "paz interior",
    ],
    "🔥 Frases de Líderes": [
        "frases de éxito",
        "frases motivadoras famosos",
        "citas inspiradoras",
        "frases líderes mundiales",
        "palabras de sabios",
        "frases celebres motivación",
        "consejos de millonarios",
        "frases de emprendedores",
        "sabiduría de vida",
        "frases para reflexionar",
    ],
    "💼 Trabajo y Carrera": [
        "motivación laboral",
        "éxito profesional",
        "crecer en el trabajo",
        "desarrollo profesional",
        "carrera exitosa",
        "motivación para trabajar",
        "liderazgo personal",
        "ser mejor profesional",
        "ascender en el trabajo",
        "pasión por el trabajo",
    ],
    "🌅 Superación de Problemas": [
        "superar obstáculos",
        "salir adelante",
        "nunca rendirse",
        "superar momentos difíciles",
        "resiliencia personal",
        "levantarse después de caer",
        "fortaleza mental",
        "superar el fracaso",
        "vencer el miedo",
        "transformar dolor en fuerza",
    ],
    "🎯 Metas y Objetivos": [
        "lograr tus metas",
        "cumplir objetivos",
        "sueños y metas",
        "alcanzar tus sueños",
        "propósito de vida",
        "visualización de metas",
        "metas claras",
        "objetivos de vida",
        "planificar el éxito",
        "enfoque en metas",
    ],
    "🧘 Paz Mental y Bienestar": [
        "paz mental",
        "tranquilidad interior",
        "bienestar emocional",
        "equilibrio vida",
        "calma interior",
        "mente tranquila",
        "serenidad personal",
        "vivir en paz",
        "soltar y avanzar",
        "mindfulness español",
    ],
}

# ================== API KEY MANAGEMENT ==================

def get_api_key() -> Optional[str]:
    """
    Retrieve API key from multiple sources (priority order):
    1. Streamlit secrets
    2. Session state (user input)
    """
    try:
        return st.secrets["YOUTUBE_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass
    
    if "api_key" in st.session_state and st.session_state.api_key:
        return st.session_state.api_key
    
    return None

# ================== CACHING DECORATORS ==================

@st.cache_data(ttl=3600, show_spinner=False)
def cached_search_shorts(keyword: str, start_date: str, region: str, api_key: str, max_results: int = 15, language: str = "es") -> Dict:
    """Cached YouTube search for Spanish content."""
    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "order": "viewCount",
        "publishedAfter": start_date,
        "maxResults": max_results,
        "videoDuration": "short",
        "regionCode": region,
        "relevanceLanguage": language,  # Prioritize Spanish content
        "key": api_key,
    }
    try:
        response = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@st.cache_data(ttl=3600, show_spinner=False)
def cached_video_details(video_ids_tuple: Tuple[str, ...], api_key: str) -> Dict:
    """Cached video details fetch."""
    params = {
        "part": "snippet,statistics,contentDetails",
        "id": ",".join(video_ids_tuple),
        "key": api_key,
    }
    try:
        response = requests.get(YOUTUBE_VIDEO_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@st.cache_data(ttl=3600, show_spinner=False)
def cached_channel_stats(channel_ids_tuple: Tuple[str, ...], api_key: str) -> Dict:
    """Cached channel stats fetch."""
    params = {
        "part": "statistics,snippet",
        "id": ",".join(channel_ids_tuple),
        "key": api_key,
    }
    try:
        response = requests.get(YOUTUBE_CHANNEL_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# ================== HELPER FUNCTIONS ==================

def parse_duration(iso_duration: str) -> str:
    """Convert ISO 8601 duration to MM:SS format."""
    if not iso_duration or not iso_duration.startswith("PT"):
        return "00:00"
    
    duration = iso_duration[2:]
    minutes = 0
    seconds = 0
    
    if "M" in duration:
        match = re.match(r'(\d+)M', duration)
        if match:
            minutes = int(match.group(1))
        duration = re.sub(r'\d+M', '', duration)
    
    if "S" in duration:
        match = re.match(r'(\d+)S', duration)
        if match:
            seconds = int(match.group(1))
    
    return f"{minutes:02d}:{seconds:02d}"

def parse_duration_seconds(iso_duration: str) -> int:
    """Convert ISO 8601 duration to total seconds."""
    if not iso_duration or not iso_duration.startswith("PT"):
        return 0
    
    duration = iso_duration[2:]
    minutes = 0
    seconds = 0
    
    if "M" in duration:
        match = re.match(r'(\d+)M', duration)
        if match:
            minutes = int(match.group(1))
        duration = re.sub(r'\d+M', '', duration)
    
    if "S" in duration:
        match = re.match(r'(\d+)S', duration)
        if match:
            seconds = int(match.group(1))
    
    return minutes * 60 + seconds

def calculate_engagement_rate(views: int, likes: int, comments: int) -> float:
    """Calculate engagement rate as percentage."""
    if views == 0:
        return 0.0
    engagement = ((likes or 0) + (comments or 0)) / views * 100
    return round(engagement, 2)

def calculate_virality_score(views: int, subs: int, days_old: int) -> float:
    """Calculate virality score (0-100)."""
    if subs == 0 or days_old == 0:
        return 0.0
    
    views_per_sub = views / max(subs, 1)
    views_per_day = views / max(days_old, 1)
    
    sub_ratio_score = min(views_per_sub * 10, 50)
    velocity_score = min(views_per_day / 1000 * 50, 50)
    
    return round(sub_ratio_score + velocity_score, 1)

def calculate_days_old(published_at: str) -> int:
    """Calculate days since video was published."""
    try:
        pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        now = datetime.now(pub_date.tzinfo)
        return (now - pub_date).days
    except:
        return 0

def generate_idea_angle_spanish(title: str, category: str, views: int, engagement: float) -> str:
    """Generate actionable idea angle in Spanish context."""
    hooks = []
    
    if views > 1000000:
        hooks.append("formato VIRAL")
    elif views > 100000:
        hooks.append("formato de alto rendimiento")
    
    if engagement > 5:
        hooks.append("gancho de alto engagement")
    
    hook_text = ", ".join(hooks) if hooks else "formato trending"
    
    return (
        f"Recrea este {hook_text} para '{category}'. "
        f"Estudia: '{title[:50]}...' - Adapta la estructura del gancho, "
        f"cambia los ejemplos, mantén un ritmo similar. "
        f"Usa voz en español neutro o específico para tu audiencia."
    )

def format_number(num: int) -> str:
    """Format large numbers for display."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

def get_virality_label(score: float) -> str:
    """Get virality tier label in Spanish."""
    if score >= 80:
        return "🔥 VIRAL"
    elif score >= 60:
        return "⚡ Muy Caliente"
    elif score >= 40:
        return "📈 Creciendo"
    elif score >= 20:
        return "✅ Bueno"
    return "📊 Normal"

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes."""
    return df.to_csv(index=False).encode("utf-8")

def convert_df_to_excel(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to Excel bytes."""
    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Shorts Ideas')
    return output.getvalue()

def is_likely_spanish(title: str, description: str) -> bool:
    """Check if content is likely in Spanish."""
    spanish_indicators = [
        # Common Spanish words
        'el', 'la', 'los', 'las', 'de', 'del', 'en', 'es', 'por', 'para',
        'que', 'con', 'como', 'cómo', 'más', 'pero', 'si', 'tu', 'tú',
        'vida', 'éxito', 'motivación', 'ser', 'estar', 'hacer', 'poder',
        'tiempo', 'día', 'mejor', 'nunca', 'siempre', 'todo', 'nada',
        # Motivation-specific
        'superación', 'mentalidad', 'disciplina', 'hábitos', 'metas',
        'sueños', 'triunfo', 'fracaso', 'esfuerzo', 'perseverancia',
        # Common endings
        'ción', 'mente', 'ando', 'iendo', 'ado', 'ido',
    ]
    
    text = (title + " " + description).lower()
    matches = sum(1 for word in spanish_indicators if word in text)
    
    return matches >= 3

# ================== SIDEBAR ==================

with st.sidebar:
    st.title("⚙️ Configuración")
    
    # API Key Section
    st.markdown("### 🔑 API Key")
    
    api_key = get_api_key()
    
    if not api_key:
        st.warning("No se encontró API key")
        user_key = st.text_input(
            "Ingresa tu YouTube API Key:",
            type="password",
            help="Obtén tu key en Google Cloud Console"
        )
        if user_key:
            st.session_state.api_key = user_key
            api_key = user_key
            st.success("✅ API key configurada")
    else:
        st.success("✅ API key lista")
        if st.button("🔄 Cambiar API Key"):
            st.session_state.api_key = ""
            st.rerun()
    
    st.markdown("---")
    
    # Search Filters
    st.markdown("### 🎯 Filtros de Búsqueda")
    
    days = st.slider(
        "Días hacia atrás:",
        min_value=1,
        max_value=30,
        value=7,
        help="Buscar videos publicados en este período"
    )
    
    region = st.selectbox(
        "Región objetivo:",
        options=list(REGION_CODES.keys()),
        index=0,
        help="Filtrar resultados por país hispanohablante"
    )
    
    results_per_keyword = st.select_slider(
        "Resultados por palabra clave:",
        options=[5, 10, 15, 20, 25],
        value=10,
        help="Más resultados = más quota de API usada"
    )
    
    st.markdown("---")
    
    # Performance Filters
    st.markdown("### 📊 Filtros de Rendimiento")
    
    min_views = st.number_input(
        "Vistas mínimas:",
        min_value=0,
        value=5000,
        step=1000,
        help="Solo mostrar videos con estas vistas mínimas"
    )
    
    max_subs = st.number_input(
        "Suscriptores máximos del canal:",
        min_value=0,
        value=50000,
        step=5000,
        help="Encontrar canales pequeños con contenido viral (0 = sin límite)"
    )
    
    min_engagement = st.slider(
        "Engagement mínimo (%):",
        min_value=0.0,
        max_value=20.0,
        value=0.0,
        step=0.5,
        help="Engagement = (likes + comentarios) / vistas × 100"
    )
    
    min_virality = st.slider(
        "Score de viralidad mínimo:",
        min_value=0,
        max_value=100,
        value=0,
        step=5,
        help="Score combinado basado en ratio vistas/subs y velocidad de crecimiento"
    )
    
    st.markdown("---")
    
    # Language Filter
    st.markdown("### 🌐 Filtro de Idioma")
    
    spanish_only = st.checkbox(
        "Solo contenido en español",
        value=True,
        help="Filtrar videos que probablemente estén en español"
    )
    
    st.markdown("---")
    
    # Duration Filter
    st.markdown("### ⏱️ Filtro de Duración")
    
    duration_range = st.slider(
        "Duración del video (segundos):",
        min_value=0,
        max_value=60,
        value=(0, 60),
        help="Filtrar Shorts por duración"
    )
    
    st.markdown("---")
    
    # Info Section
    st.markdown("### 💡 Tips Pro")
    st.info(
        "**Encontrar oportunidades virales:**\n"
        "• Pocos subs + Muchas vistas = Contenido viral\n"
        "• Alto engagement = Buenos ganchos\n"
        "• Alto score viralidad = Replicable\n\n"
        "**Mejor hora para publicar:**\n"
        "• España: 14:00-16:00, 20:00-22:00\n"
        "• LATAM: 12:00-14:00, 19:00-21:00"
    )

# ================== MAIN CONTENT ==================

# Header with Spanish flag colors
st.markdown('<div class="spanish-header"></div>', unsafe_allow_html=True)

st.title("🇪🇸 Spanish Motivation Shorts Finder")
st.markdown(
    "Encuentra **Shorts virales de motivación en español** de **canales pequeños**, "
    "analiza su rendimiento y obtén ideas accionables para tu propio contenido."
)

# Quick Stats Banner
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🌎 Regiones", "20 países")
with col2:
    st.metric("📂 Categorías", "12 nichos")
with col3:
    st.metric("🔑 Keywords", "120+ términos")
with col4:
    st.metric("🎯 Enfoque", "100% Español")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🔍 Buscar", "📊 Análisis", "💡 Ideas de Contenido", "ℹ️ Cómo Usar"])

with tab1:
    # Category Selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        category = st.selectbox(
            "🎯 Elige tu categoría de motivación:",
            list(NICHE_KEYWORDS.keys()),
            help="Cada categoría tiene palabras clave optimizadas en español"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        show_keywords = st.checkbox("Mostrar palabras clave", value=False)
    
    if show_keywords:
        st.caption(f"**Palabras clave para {category}:**")
        keywords_list = NICHE_KEYWORDS[category]
        cols = st.columns(3)
        for i, kw in enumerate(keywords_list):
            cols[i % 3].write(f"• {kw}")
    
    # Custom Keywords
    with st.expander("➕ Agregar Palabras Clave Personalizadas (Opcional)"):
        custom_keywords = st.text_area(
            "Ingresa palabras clave adicionales (una por línea):",
            placeholder="motivación gym\néxito empresarial\nmentalidad de tiburón",
            height=100
        )
        st.caption("💡 Tip: Usa términos específicos de tu nicho en español")
    
    # Multi-region search option
    with st.expander("🌎 Búsqueda Multi-Región (Opcional)"):
        multi_region = st.checkbox(
            "Buscar en múltiples países",
            value=False,
            help="Buscar en varios países hispanohablantes a la vez"
        )
        
        if multi_region:
            selected_regions = st.multiselect(
                "Selecciona países:",
                options=list(REGION_CODES.keys()),
                default=["🇪🇸 España (Spain)", "🇲🇽 México", "🇦🇷 Argentina"]
            )
        else:
            selected_regions = [region]
    
    # Search Button
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_btn = st.button(
            "🚀 Buscar Shorts Virales",
            type="primary",
            use_container_width=True,
            disabled=not api_key
        )

    # ================== SEARCH EXECUTION ==================
    
    if search_btn:
        if not api_key:
            st.error("❌ Por favor configura tu YouTube API key en la barra lateral")
        else:
            # Prepare keywords
            keywords = NICHE_KEYWORDS.get(category, []).copy()
            if custom_keywords:
                custom_list = [kw.strip() for kw in custom_keywords.split('\n') if kw.strip()]
                keywords.extend(custom_list)
            
            # Calculate date range
            start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
            
            # Get regions to search
            if multi_region and selected_regions:
                regions_to_search = [(r, REGION_CODES[r]) for r in selected_regions]
            else:
                regions_to_search = [(region, REGION_CODES[region])]
            
            # Progress tracking
            total_searches = len(keywords) * len(regions_to_search)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            all_rows = []
            seen_video_ids = set()
            errors = []
            search_count = 0
            
            for region_name, region_code in regions_to_search:
                for kw in keywords:
                    search_count += 1
                    progress = search_count / total_searches
                    progress_bar.progress(progress)
                    status_text.text(f"🔎 Buscando: {kw} en {region_name} ({search_count}/{total_searches})")
                    
                    # Search for videos
                    search_data = cached_search_shorts(
                        kw, start_date, region_code, api_key, 
                        results_per_keyword, language="es"
                    )
                    
                    if "error" in search_data:
                        errors.append(f"Error en '{kw}': {search_data['error']}")
                        continue
                    
                    if "items" not in search_data or not search_data["items"]:
                        continue
                    
                    videos = search_data["items"]
                    video_ids = [v["id"]["videoId"] for v in videos if v["id"]["videoId"] not in seen_video_ids]
                    channel_ids = list(set([v["snippet"]["channelId"] for v in videos]))
                    
                    if not video_ids:
                        continue
                    
                    seen_video_ids.update(video_ids)
                    
                    # Fetch detailed data
                    vid_details = cached_video_details(tuple(video_ids), api_key)
                    chan_details = cached_channel_stats(tuple(channel_ids), api_key)
                    
                    if "error" in vid_details or "error" in chan_details:
                        continue
                    
                    vid_map = {item["id"]: item for item in vid_details.get("items", [])}
                    chan_map = {item["id"]: item for item in chan_details.get("items", [])}
                    
                    # Process each video
                    for v in videos:
                        vid_id = v["id"]["videoId"]
                        ch_id = v["snippet"]["channelId"]
                        
                        if vid_id not in vid_map:
                            continue
                        
                        v_detail = vid_map.get(vid_id, {})
                        c_detail = chan_map.get(ch_id, {})
                        
                        v_snippet = v_detail.get("snippet", {})
                        v_stats = v_detail.get("statistics", {})
                        v_content = v_detail.get("contentDetails", {})
                        c_stats = c_detail.get("statistics", {})
                        c_snippet = c_detail.get("snippet", {})
                        
                        # Extract data
                        title = v_snippet.get("title", "")
                        description = v_snippet.get("description", "")
                        
                        # Spanish language filter
                        if spanish_only and not is_likely_spanish(title, description):
                            continue
                        
                        # Extract metrics
                        views = int(v_stats.get("viewCount", 0))
                        likes = int(v_stats.get("likeCount", 0)) if "likeCount" in v_stats else 0
                        comments = int(v_stats.get("commentCount", 0)) if "commentCount" in v_stats else 0
                        subs = int(c_stats.get("subscriberCount", 0)) if "subscriberCount" in c_stats else 0
                        
                        # Duration check
                        duration_sec = parse_duration_seconds(v_content.get("duration", ""))
                        if duration_sec < duration_range[0] or duration_sec > duration_range[1]:
                            continue
                        
                        # Calculate derived metrics
                        published_at = v_snippet.get("publishedAt", "")
                        days_old = calculate_days_old(published_at)
                        engagement_rate = calculate_engagement_rate(views, likes, comments)
                        virality_score = calculate_virality_score(views, subs, max(days_old, 1))
                        views_per_day = views / max(days_old, 1)
                        
                        # Apply filters
                        if views < min_views:
                            continue
                        if max_subs > 0 and subs > max_subs:
                            continue
                        if engagement_rate < min_engagement:
                            continue
                        if virality_score < min_virality:
                            continue
                        
                        # Build row
                        tags = v_snippet.get("tags", [])
                        thumbnails = v_snippet.get("thumbnails", {})
                        channel_country = c_snippet.get("country", "N/A")
                        
                        all_rows.append({
                            # Identifiers
                            "Video ID": vid_id,
                            "Título": title,
                            "URL del Video": f"https://youtube.com/shorts/{vid_id}",
                            
                            # Performance
                            "Vistas": views,
                            "Likes": likes,
                            "Comentarios": comments,
                            "Engagement (%)": engagement_rate,
                            "Score Viralidad": virality_score,
                            "Nivel Viralidad": get_virality_label(virality_score),
                            "Vistas/Día": round(views_per_day, 0),
                            
                            # Video Details
                            "Duración": parse_duration(v_content.get("duration", "")),
                            "Duración (seg)": duration_sec,
                            "Publicado": published_at[:10] if published_at else "",
                            "Días Online": days_old,
                            "Descripción": description[:300],
                            "Tags": ", ".join(tags[:10]) if tags else "",
                            
                            # Thumbnail
                            "Thumbnail": thumbnails.get("high", {}).get("url", thumbnails.get("default", {}).get("url", "")),
                            
                            # Channel
                            "Canal": v_snippet.get("channelTitle", ""),
                            "URL del Canal": f"https://youtube.com/channel/{ch_id}",
                            "Suscriptores": subs,
                            "País del Canal": channel_country,
                            
                            # Meta
                            "Categoría": category,
                            "Palabra Clave": kw,
                            "Región Búsqueda": region_name,
                            
                            # Actionable
                            "Ángulo de Idea": generate_idea_angle_spanish(title, category, views, engagement_rate),
                        })
                    
                    time.sleep(0.1)
            
            progress_bar.empty()
            status_text.empty()
            
            # Show errors
            if errors:
                with st.expander(f"⚠️ {len(errors)} advertencias"):
                    for err in errors:
                        st.warning(err)
            
            # Process results
            if all_rows:
                results_df = pd.DataFrame(all_rows)
                results_df = results_df.sort_values(
                    by=["Score Viralidad", "Vistas"],
                    ascending=[False, False]
                ).reset_index(drop=True)
                
                st.session_state.results_df = results_df
                st.session_state.search_completed = True
                
                # Summary
                st.markdown("---")
                st.subheader("📊 Resumen de Resultados")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Videos Encontrados", len(results_df))
                with col2:
                    st.metric("Vistas Promedio", format_number(int(results_df["Vistas"].mean())))
                with col3:
                    st.metric("Engagement Promedio", f"{results_df['Engagement (%)'].mean():.2f}%")
                with col4:
                    viral_count = len(results_df[results_df["Score Viralidad"] >= 60])
                    st.metric("Videos Virales", viral_count)
                with col5:
                    st.metric("Viralidad Promedio", f"{results_df['Score Viralidad'].mean():.1f}")
                
                # Results Table
                st.markdown("---")
                st.subheader("🎬 Resultados de Videos")
                
                display_cols = st.multiselect(
                    "Columnas a mostrar:",
                    options=results_df.columns.tolist(),
                    default=[
                        "Título", "Vistas", "Engagement (%)", 
                        "Nivel Viralidad", "Canal", "Suscriptores", "URL del Video"
                    ]
                )
                
                if display_cols:
                    st.dataframe(
                        results_df[display_cols],
                        use_container_width=True,
                        height=400,
                        column_config={
                            "URL del Video": st.column_config.LinkColumn("URL del Video"),
                            "URL del Canal": st.column_config.LinkColumn("URL del Canal"),
                            "Thumbnail": st.column_config.ImageColumn("Thumbnail", width="medium"),
                            "Vistas": st.column_config.NumberColumn("Vistas", format="%d"),
                            "Score Viralidad": st.column_config.ProgressColumn(
                                "Score Viralidad",
                                min_value=0,
                                max_value=100,
                            ),
                        }
                    )
                
                # Download Options
                st.markdown("---")
                st.subheader("📥 Exportar Resultados")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        "📄 Descargar CSV",
                        data=convert_df_to_csv(results_df),
                        file_name=f"shorts_motivacion_esp_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    try:
                        excel_data = convert_df_to_excel(results_df)
                        st.download_button(
                            "📊 Descargar Excel",
                            data=excel_data,
                            file_name=f"shorts_motivacion_esp_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except ImportError:
                        st.info("Instala openpyxl para exportar a Excel")
                
                with col3:
                    st.download_button(
                        "📋 Descargar JSON",
                        data=results_df.to_json(orient="records", indent=2, force_ascii=False),
                        file_name=f"shorts_motivacion_esp_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            else:
                st.warning(
                    "No se encontraron videos con tus filtros. Intenta:\n"
                    "- Aumentar días de búsqueda\n"
                    "- Reducir vistas mínimas\n"
                    "- Aumentar suscriptores máximos\n"
                    "- Reducir engagement/viralidad mínimos\n"
                    "- Desactivar filtro 'Solo español'"
                )

with tab2:
    st.subheader("📊 Dashboard de Análisis")
    
    if "results_df" in st.session_state and not st.session_state.results_df.empty:
        df = st.session_state.results_df
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Distribución de Vistas (Top 20 canales pequeños)")
            st.bar_chart(df.nsmallest(20, 'Suscriptores').set_index('Título')['Vistas'])
        
        with col2:
            st.markdown("#### Distribución por Nivel de Viralidad")
            virality_dist = df['Nivel Viralidad'].value_counts()
            st.bar_chart(virality_dist)
        
        st.markdown("---")
        
        # Top Performers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top 5 por Viralidad")
            top_viral = df.nlargest(5, 'Score Viralidad')[['Título', 'Vistas', 'Score Viralidad', 'Canal']]
            st.dataframe(top_viral, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### 💬 Top 5 por Engagement")
            top_engage = df.nlargest(5, 'Engagement (%)')[['Título', 'Vistas', 'Engagement (%)', 'Canal']]
            st.dataframe(top_engage, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Keyword Performance
        st.markdown("#### 🔍 Rendimiento por Palabra Clave")
        keyword_stats = df.groupby('Palabra Clave').agg({
            'Vistas': 'mean',
            'Score Viralidad': 'mean',
            'Video ID': 'count'
        }).rename(columns={'Video ID': 'Videos Encontrados'}).round(1)
        st.dataframe(keyword_stats.sort_values('Score Viralidad', ascending=False), use_container_width=True)
        
        # Country Distribution
        if 'País del Canal' in df.columns:
            st.markdown("#### 🌎 Distribución por País del Canal")
            country_dist = df['País del Canal'].value_counts()
            st.bar_chart(country_dist)
        
    else:
        st.info("¡Ejecuta una búsqueda primero para ver el análisis!")

with tab3:
    st.subheader("💡 Generador de Ideas de Contenido")
    
    st.markdown("""
    ### 🎬 Plantillas de Contenido para Motivación en Español
    
    Basado en los formatos más virales encontrados, aquí tienes plantillas que puedes usar:
    """)
    
    # Content Templates
    templates = {
        "🎯 Gancho + Historia + Lección": {
            "estructura": "1. Gancho impactante (3 seg)\n2. Historia corta (20-30 seg)\n3. Lección poderosa (10-15 seg)\n4. Call to action",
            "ejemplo": "'¿Sabías que el 90% de millonarios se levanta antes de las 6am?' → Historia de alguien exitoso → Tu rutina matutina puede cambiar tu vida",
            "duracion": "45-55 segundos"
        },
        "📊 Dato Impactante + Explicación": {
            "estructura": "1. Estadística sorprendente (3 seg)\n2. Por qué es importante (15-20 seg)\n3. Qué puedes hacer al respecto (15-20 seg)",
            "ejemplo": "'Solo el 3% de personas escriben sus metas' → Estudios muestran que escribir multiplica probabilidad de éxito → 3 pasos para empezar hoy",
            "duracion": "35-45 segundos"
        },
        "💭 Frase + Contexto + Aplicación": {
            "estructura": "1. Frase famosa (5 seg)\n2. Quién la dijo y contexto (15 seg)\n3. Cómo aplicarla en tu vida (20-25 seg)",
            "ejemplo": "'El éxito es la suma de pequeños esfuerzos repetidos día tras día' - Robert Collier → Su historia → Tu próximo pequeño paso",
            "duracion": "40-50 segundos"
        },
        "❌ Error Común + Solución": {
            "estructura": "1. Error que todos cometen (5 seg)\n2. Por qué es un error (15-20 seg)\n3. La manera correcta (20-25 seg)",
            "ejemplo": "'El error #1 que arruina tus metas' → Fijarse en resultados, no en sistemas → Cómo crear sistemas que funcionan",
            "duracion": "45-55 segundos"
        },
        "🔄 Antes vs Después (Mentalidad)": {
            "estructura": "1. Mentalidad común/pobre (15 seg)\n2. Mentalidad de éxito (15 seg)\n3. Cómo hacer el cambio (15-20 seg)",
            "ejemplo": "'Persona promedio piensa en excusas' vs 'Persona exitosa piensa en soluciones' → El switch mental que necesitas",
            "duracion": "45-50 segundos"
        },
    }
    
    for template_name, template_data in templates.items():
        with st.expander(template_name):
            st.markdown(f"**📋 Estructura:**\n{template_data['estructura']}")
            st.markdown(f"**💡 Ejemplo:**\n{template_data['ejemplo']}")
            st.markdown(f"**⏱️ Duración ideal:** {template_data['duracion']}")
    
    st.markdown("---")
    
    # Trending Hooks in Spanish
    st.markdown("### 🎣 Ganchos Virales en Español")
    
    hooks = [
        "🔥 'La verdad que nadie te dice sobre...'",
        "🔥 '¿Por qué el 99% de personas nunca...'",
        "🔥 'El secreto que los millonarios no quieren que sepas'",
        "🔥 'Esto es lo que diferencia a los exitosos'",
        "🔥 'Si estás viendo esto, no es coincidencia'",
        "🔥 'Escucha esto si sientes que no avanzas'",
        "🔥 'El error que está arruinando tu vida'",
        "🔥 'Nadie te enseñó esto sobre el dinero'",
        "🔥 'Tu problema no es la motivación, es...'",
        "🔥 'Lo que aprendí perdiendo todo'",
        "🔥 '3 señales de que serás exitoso'",
        "🔥 'Este hábito cambió mi vida en 30 días'",
    ]
    
    cols = st.columns(2)
    for i, hook in enumerate(hooks):
        cols[i % 2].write(hook)
    
    st.markdown("---")
    
    # Voice-over tips
    st.markdown("### 🎙️ Tips para Voz en Español")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Español Neutro (Recomendado):**
        - Sin acentos regionales marcados
        - Vocabulario universal
        - Ideal para audiencia de toda Latinoamérica + España
        - Herramientas: ElevenLabs, Murf.ai, Amazon Polly
        """)
    
    with col2:
        st.markdown("""
        **Según tu audiencia objetivo:**
        - 🇲🇽 México: Tono más cálido, expresivo
        - 🇪🇸 España: Más directo, "vosotros"
        - 🇦🇷 Argentina: Distintivo "vos", más informal
        - 🇨🇴 Colombia: Neutro, muy claro
        """)

with tab4:
    st.subheader("📖 Cómo Usar Esta Herramienta")
    
    st.markdown("""
    ### 🎯 Encontrar Ideas Virales de Motivación en Español
    
    1. **Selecciona una Categoría** - Elige entre 12 nichos de motivación
    2. **Ajusta los Filtros** - Usa la barra lateral para refinar resultados
    3. **Analiza Resultados** - Busca alto score de viralidad con pocos suscriptores
    4. **Exporta y Ejecuta** - Descarga ideas y crea tu contenido
    
    ---
    
    ### 📊 Entendiendo las Métricas
    
    | Métrica | Significado | Valor Bueno |
    |---------|-------------|-------------|
    | **Score Viralidad** | Rendimiento relativo al tamaño del canal | 60+ = Viral |
    | **Engagement (%)** | (Likes + Comentarios) / Vistas × 100 | 3%+ = Bueno |
    | **Vistas/Día** | Promedio de vistas diarias desde publicación | 10K+ = Trending |
    
    ---
    
    ### 🌎 Mejores Prácticas para Español
    
    **Audiencia por País:**
    - 🇲🇽 México: Mayor mercado hispanohablante en YouTube
    - 🇪🇸 España: Alto poder adquisitivo
    - 🇦🇷 Argentina: Muy activos en redes
    - 🇨🇴 Colombia: Crecimiento rápido
    
    **Horarios Óptimos (Hora Local):**
    - Mañana: 7:00 - 9:00
    - Tarde: 12:00 - 14:00
    - Noche: 19:00 - 22:00
    
    ---
    
    ### 💰 Ideas de Monetización
    
    - **Canal Faceless**: Crea contenido con IA y voz sintética
    - **Vender Listas de Ideas**: Ofrece CSVs semanales a creadores
    - **Servicios de Automatización**: Research + Scripts + Edición
    - **Coaching**: Enseña a encontrar y replicar contenido viral
    
    ---
    
    ### 🔑 Obtener tu API Key
    
    1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
    2. Crea un nuevo proyecto
    3. Habilita **YouTube Data API v3**
    4. Crea credenciales → API Key
    5. Agrégala en secretos de Streamlit o pégala en la barra lateral
    
    ---
    
    ### 🔒 Almacenar API Key de Forma Segura
    
    Para deployment, crea `.streamlit/secrets.toml`:
    ```toml
    YOUTUBE_API_KEY = "tu-api-key-aquí"
    ```
    """)

# ================== FOOTER ==================

st.markdown("---")

# Quick stats about the tool
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🎯 Enfocado en:**
    - Motivación en español
    - Éxito y superación
    - Mentalidad millonaria
    """)

with col2:
    st.markdown("""
    **🌎 Cobertura:**
    - 20 países hispanohablantes
    - 12 categorías de contenido
    - 120+ palabras clave
    """)

with col3:
    st.markdown("""
    **📊 Métricas:**
    - Score de viralidad
    - Análisis de engagement
    - Detección de español
    """)

st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Hecho con ❤️ para creadores de contenido en español | 
        <a href='https://developers.google.com/youtube/v3' target='_blank'>YouTube API Docs</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
