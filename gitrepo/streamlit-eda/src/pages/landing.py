import streamlit as st
from .registry import page


@page("landing", title="랜딩", description="랜딩 화면")
def render(_: dict | None = None):
    # 전체 화면을 덮는 스플래시(랜딩) 섹션 + 미묘한 배경 애니메이션
    st.markdown(
        """
        <style>
        .splash { position: fixed; inset: 0; background: #1e3a8a; display: flex; align-items: center; justify-content: center; z-index: 1; }
        .splash::before {
            content: "";
            position: absolute; inset: -20%;
            background:
              radial-gradient(600px 600px at 20% 30%, rgba(255,255,255,0.08), transparent 60%),
              radial-gradient(600px 600px at 80% 70%, rgba(255,255,255,0.06), transparent 60%);
            animation: bg-move 9s ease-in-out infinite alternate;
        }
        @keyframes bg-move { to { background-position: 30% 40%, 70% 60%; } }

        .splash-inner { position: relative; text-align: center; color: #fff; padding: 24px; }
        .splash-title-1 { margin: 0; font-size: 56px; font-weight: 800; letter-spacing: .3px; animation: fadeUp .7s ease-out both; }
        .splash-title-2 { margin: 10px 0 0 0; font-size: 40px; font-weight: 800; animation: fadeUp .7s .08s ease-out both; }
        .splash-btn { display: inline-block; margin-top: 28px; padding: 12px 28px; border-radius: 9999px; background: #e5e7eb; color: #111827; font-weight: 700; text-decoration: none; box-shadow: 0 4px 14px rgba(0,0,0,.18); transition: transform .2s ease, background .2s ease; animation: fadeUp .7s .16s ease-out both; }
        .splash-btn:hover { background:#d1d5db; transform: translateY(-1px); }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(12px) scale(.98);} to { opacity:1; transform: translateY(0) scale(1);} }
        </style>

        <div class="splash">
          <div class="splash-inner">
            <h1 class="splash-title-1">KOSSDA, ISDS</h1>
            <h2 class="splash-title-2">2025 [한국사회, 시선]</h2>
            <a class="splash-btn" href="?page=main" target="_self">보고서 살펴보기</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
