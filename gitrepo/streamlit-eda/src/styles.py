def global_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');
:root {
    --brand-dark: #0f172a;
    --brand-primary: #1e3a8a;
    --brand-accent: #3b82f6;
    --surface: #ffffff;
    --surface-muted: #f1f5f9;
    color-scheme: light;
}

html {
    scroll-behavior: smooth;
}

html,
body,
[data-testid="stAppViewContainer"],
main,
.main,
.main .block-container {
    background: var(--surface-muted) !important;
    color: var(--brand-dark);
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="collapsedControl"] {
    background: var(--surface-muted) !important;
}

.story-content,
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] span,
.stDownloadButton>button,
.stButton>button,
.stRadio div[role="radiogroup"] > label,
.stMarkdown,
.stCaption {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 4rem;
    max-width: 1100px;
}

.app-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 0.75rem;
    margin-bottom: 0.75rem;
    border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.brand__logo {
    display: inline-flex;
    width: 40px;
    height: 40px;
    align-items: center;
    justify-content: center;
    border-radius: 14px;
    background: var(--brand-dark);
    color: #fff;
    font-weight: 700;
    font-size: 1.05rem;
}

.brand__name {
    font-weight: 800;
    font-size: 1.1rem;
}

.brand__tagline {
    font-size: 0.78rem;
    color: rgba(15, 23, 42, 0.6);
}

.stRadio > label { display: none; }
.stRadio div[role="radiogroup"] {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: flex-end;
}

.stRadio div[role="radiogroup"] > label {
    background: rgba(15, 23, 42, 0.06);
    border: 1px solid transparent;
    border-radius: 999px;
    padding: 0.45rem 0.95rem;
    font-weight: 600;
    color: var(--brand-dark);
    transition: all 0.2s ease;
}

.stRadio div[role="radiogroup"] > label:hover {
    border-color: rgba(30, 64, 175, 0.25);
}

.stRadio div[role="radiogroup"] > label > div[role="radio"][aria-checked="true"] {
    background: var(--brand-dark);
    color: #fff;
    border-radius: 999px;
    padding: 0.2rem 0.65rem;
}

.hero-card {
    background: linear-gradient(135deg, rgba(30, 64, 175, 0.9), rgba(59, 130, 246, 0.85));
    border-radius: 24px;
    padding: 3rem;
    color: #fff;
    position: relative;
    overflow: hidden;
    margin-bottom: 2.5rem;
    box-shadow: 0 24px 48px rgba(30, 64, 175, 0.25);
}

.hero-card::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 18% 22%, rgba(255, 255, 255, 0.2), transparent 55%),
                radial-gradient(circle at 75% 18%, rgba(255, 255, 255, 0.18), transparent 55%);
    opacity: 0.7;
}

.hero-card__text {
    position: relative;
    z-index: 2;
    max-width: 560px;
}

.hero-chip {
    display: inline-flex;
    align-items: center;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.18);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.hero-card h1 {
    margin: 1rem 0 0.75rem;
    font-size: 2.35rem;
    font-weight: 800;
    line-height: 1.2;
}

.hero-card p {
    margin: 0;
    font-size: 1rem;
    line-height: 1.7;
}

.hero-sub {
    margin-top: 1rem;
    font-size: 0.9rem;
    opacity: 0.85;
}

.mini-card {
    background: var(--surface);
    padding: 1.1rem;
    border-radius: 16px;
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    margin-bottom: 0.75rem;
}

.mini-card__meta {
    font-size: 0.82rem;
    font-weight: 700;
    color: rgba(15, 23, 42, 0.7);
}

.mini-card__title {
    font-size: 0.92rem;
    font-weight: 600;
    margin-top: 0.35rem;
    color: var(--brand-dark);
}

.story-card {
    background: var(--surface);
    border-radius: 20px;
    padding: 1.6rem;
    border: 1px solid rgba(148, 163, 184, 0.22);
    box-shadow: 0 18px 36px rgba(15, 23, 42, 0.12);
    min-height: 220px;
}

.story-card__topic {
    display: inline-flex;
    padding: 0.35rem 0.8rem;
    border-radius: 999px;
    background: rgba(30, 64, 175, 0.1);
    color: var(--brand-primary);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}

.story-card h3 {
    margin: 1rem 0 0.5rem;
    font-size: 1.08rem;
    font-weight: 700;
    color: var(--brand-dark);
}

.story-card p {
    font-size: 0.9rem;
    color: rgba(15, 23, 42, 0.72);
    line-height: 1.6;
}

.story-card__meta {
    margin-top: 0.75rem;
    font-size: 0.75rem;
    color: rgba(15, 23, 42, 0.55);
}

.topic-card {
    background: var(--surface);
    border-radius: 24px;
    padding: 1.6rem;
    border: 1px solid rgba(148, 163, 184, 0.25);
    min-height: 320px;
    display: flex;
    flex-direction: column;
    gap: 1.1rem;
    box-shadow: 0 14px 32px rgba(15, 23, 42, 0.1);
    position: relative;
    overflow: hidden;
}

.topic-card__icon {
    width: 52px;
    height: 52px;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 1.3rem;
    font-weight: 700;
}

.topic-card__body h3 {
    margin: 0;
    font-size: 1.15rem;
    font-weight: 700;
}

.topic-card__body p {
    margin: 0.5rem 0 0;
    font-size: 0.92rem;
    color: rgba(15, 23, 42, 0.75);
    line-height: 1.55;
}

.topic-card__footer {
    margin-top: 0.75rem;
    font-size: 0.8rem;
    color: rgba(15, 23, 42, 0.6);
    font-weight: 600;
}

.topic-card__preview {
    margin-top: auto;
    font-size: 0.85rem;
    line-height: 1.5;
    color: rgba(15, 23, 42, 0.68);
    background: rgba(15, 23, 42, 0.04);
    padding: 0.75rem;
    border-radius: 12px;
}

.timeline-row {
    display: flex;
    gap: 1rem;
    padding: 0.85rem 0;
    align-items: flex-start;
}

.timeline-dot {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    background: var(--brand-primary);
    margin-top: 0.4rem;
}

.timeline-year {
    font-weight: 700;
    font-size: 0.9rem;
}

.timeline-text {
    font-size: 0.88rem;
    color: rgba(15, 23, 42, 0.7);
}

.archive-card {
    background: var(--surface);
    border-radius: 18px;
    padding: 1.4rem;
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 16px 34px rgba(15, 23, 42, 0.12);
    min-height: 240px;
}

.archive-card__tag {
    display: inline-flex;
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    background: rgba(30, 64, 175, 0.12);
    color: var(--brand-primary);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.archive-card h3 {
    margin: 0.9rem 0 0.45rem;
    font-size: 1.02rem;
    font-weight: 700;
}

.archive-card p {
    margin: 0;
    font-size: 0.86rem;
    line-height: 1.55;
    color: rgba(15, 23, 42, 0.72);
}

.archive-card__meta {
    margin-top: 0.75rem;
    font-size: 0.75rem;
    color: rgba(15, 23, 42, 0.55);
}

.about-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
}

.about-card {
    background: var(--surface);
    border-radius: 20px;
    padding: 1.6rem;
    border: 1px solid rgba(148, 163, 184, 0.25);
    box-shadow: 0 16px 32px rgba(15, 23, 42, 0.12);
}

.about-card h4 {
    margin: 0;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--brand-dark);
}

.about-card p {
    margin: 0.75rem 0 0;
    font-size: 0.9rem;
    line-height: 1.65;
    color: rgba(15, 23, 42, 0.75);
}

.about-links {
    display: flex;
    gap: 0.75rem;
    margin-top: 1rem;
}

.about-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.55rem 1.15rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    text-decoration: none;
    border: 1px solid rgba(30, 64, 175, 0.25);
    color: var(--brand-dark);
    transition: all 0.2s ease;
}

.about-link:hover {
    border-color: var(--brand-primary);
}

.about-link--primary {
    background: var(--brand-dark);
    color: #fff;
    border: none;
}

.story-content {
    max-width: 880px;
    margin: 0 auto 2.8rem;
    color: var(--brand-dark);
    line-height: 1.78;
    font-size: 1.05rem;
}

.chart-note {
    font-size: 0.78rem;
    color: rgba(15, 23, 42, 0.55);
    text-align: center;
    margin-top: -1.2rem;
}

.story-figure {
    max-width: 880px;
    margin: 1.8rem auto;
    padding: 0;
}

.story-figure div[data-testid="stPlotlyChartContainer"] {
    width: 100% !important;
    margin: 0 auto;
}

.story-caption {
    font-size: 0.78rem;
    color: rgba(15, 23, 42, 0.55);
    text-align: center;
    margin-top: -0.4rem;
}

.story-content h1 { font-size: 2.2rem; margin: 0 0 1.2rem 0; font-weight: 800; }
.story-content h2 { font-size: 1.8rem; margin: 2.4rem 0 1rem 0; font-weight: 800; }
.story-content h3 { font-size: 1.4rem; margin: 1.8rem 0 0.8rem 0; font-weight: 700; color: var(--brand-primary); }
.story-content h4 { font-size: 1.15rem; margin: 1.4rem 0 0.6rem 0; font-weight: 700; color: var(--brand-primary); }
.story-content p { margin: 0 0 1.1rem 0; }
.story-content ul, .story-content ol { padding-left: 1.5rem; margin: 0 0 1.2rem 0; }
.story-content li { margin-bottom: 0.4rem; }
.story-content strong { color: var(--brand-dark); }
.story-content blockquote {
    margin: 1.6rem 0;
    padding: 1rem 1.2rem;
    border-left: 4px solid var(--brand-primary);
    background: rgba(30, 64, 175, 0.08);
    border-radius: 8px;
}
.story-content table { width: 100%; border-collapse: collapse; margin: 1.8rem 0; font-size: 0.95rem; }
.story-content table th,
.story-content table td { border: 1px solid #e5e7eb; padding: 0.6rem 0.75rem; text-align: center; }
.story-content table th { background: #f8fafc; font-weight: 700; color: var(--brand-primary); }

.stButton>button {
    border-radius: 999px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    padding: 0.55rem 1rem;
    font-weight: 600;
}

.stDownloadButton>button {
    border-radius: 12px;
    background: rgba(15, 23, 42, 0.85);
    color: #fff;
    font-weight: 600;
}
    </style>
    """
