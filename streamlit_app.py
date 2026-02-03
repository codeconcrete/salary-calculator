import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 디자인 (모바일 최적화 + 강제 화이트)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="일용직 계산기", page_icon="🏗️", layout="centered")

hide_st_style = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
            
            /* [모바일 최적화] 좌우 여백 줄이기 & 상단 여백 축소 */
            .block-container {
                padding-top: 2rem;
                padding-bottom: 5rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }
            
            /* [색상 강제 통일] 모든 글씨 무조건 흰색 */
            html, body, [class*="css"], div, span, p, label, h1, h2, h3, h4, h5, h6 {
                font-family: 'Noto Sans KR', sans-serif;
                color: #ffffff !important;
            }
            
            /* 메인 배경 */
            .stApp { background-color: #1a1a1a; }
            
            /* [입력창 스타일] 글씨 흰색 + 배경 진회색 */
            .stNumberInput input {
                background-color: #333333 !important;
                color: #ffffff !important;
                font-weight: bold;
                border: 1px solid #555555;
            }
            
            /* 라벨 & 선택지 글씨 */
            .stNumberInput label, .stRadio label, .stCheckbox label {
                color: #ffffff !important;
                font-weight: bold;
            }
            .stRadio div[role='radiogroup'] > label {
                color: #ffffff !important;
            }
            .stRadio p, .stCheckbox p {
                color: #ffffff !important;
            }

            /* [버튼 스타일] 모바일 터치하기 좋게 큼직하게 */
            div.stButton > button {
                background-color: #0085ff;
                color: white !important;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                width: 100%;
                padding: 15px 0; /* 위아래 높이 키움 */
                margin-top: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            }
            div.stButton > button:hover {
                background-color: #0066cc;
                border: 1px solid #ffffff;
            }
            
            /* 결과 박스 디자인 */
            .result-box {
                background-color: #262626;
                padding: 20px;
                border-radius: 12px;
                border: 1px solid #444;
                border-left: 6px solid #0085ff;
                margin-top: 20px;
            }
            
            /* 자세히 보기(Expander) 내부 스타일 */
            .streamlit-expanderHeader {
                background-color: #333333 !important;
                color: #ffffff !important;
                border-radius: 8px;
            }
            .streamlit-expanderContent {
                background-color: #262626 !important;
                color: #ffffff !important;
            }

            /* 안내 문구 박스 (Info) 스타일 */
            .stAlert {
                background-color: #222222 !important;
                color: #ffffff !important;
                border: 1px solid #444;
            }
            
            /* 불필요 요소 숨김 */
            #MainMenu, footer, header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 타이틀 영역
# -----------------------------------------------------------------------------
st.markdown("<h3 style='text-align: center; color: #ffffff;'>🏗️ 일용직 실수령액 계산기</h3>", unsafe_allow_html=True)
st.write("---")

# -----------------------------------------------------------------------------
# 3. 입력 영역 (UI)
# -----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    # 모바일 화면 고려하여 라벨을 짧게 수정
    daily_wage = st.number_input("일당 (원)", value=180000, step=10000, format="%d")

with col2:
    work_days = st.number_input("공수 (일)", value=20.0, step=0.5, format="%.1f")

st.write("") # 간격

# 공제 방식 선택 (모바일에서는 세로 배치가 보기 좋음)
calc_type = st.radio(
    "공제 방식 선택",
    ("일반 건설 일용직 (4대보험+세금)", "3.3% 공제 (프리랜서/인력사무소)"),
    horizontal=False # 세로로 배치하여 글자 잘림 방지
)

# 8일 이상 근무 여부
if calc_type == "일반 건설 일용직 (4대보험+세금)":
    st.write("")
    apply_insurance = st.checkbox("월 8일 이상 근무 (국민/건강 적용)", value=True)
else:
    apply_insurance = False

# -----------------------------------------------------------------------------
# 4. 계산 로직
# -----------------------------------------------------------------------------
if st.button("계산하기 💸"):
    total_gross = daily_wage * work_days # 총 급여(세전)
    deductions = {} 
    
    total_deduction = 0
    
    if calc_type == "3.3% 공제 (프리랜서/인력사무소)":
        tax = total_gross * 0.033
        deductions['사업소득세(3.3%)'] = tax
        total_deduction = tax
        
    else: # 일반 건설 일용직
        # 소득세 (일당 15만원 비과세)
        taxable_daily = max(0, daily_wage - 150000)
        daily_income_tax = taxable_daily * 0.06 * 0.45
        daily_local_tax = daily_income_tax * 0.1
        
        total_income_tax = int(daily_income_tax * work_days)
        total_local_tax = int(daily_local_tax * work_days)
        
        # 4대 보험
        emp_ins = int(total_gross * 0.009) # 고용
        
        pension_ins = 0
        health_ins = 0
        care_ins = 0
        
        if apply_insurance:
            pension_ins = int(total_gross * 0.045) # 국민
            health_ins = int(total_gross * 0.03545) # 건강
            care_ins = int(health_ins * 0.1295) # 요양
            
        deductions['고용보험(0.9%)'] = emp_ins
        if apply_insurance:
            deductions['국민연금(4.5%)'] = pension_ins
            deductions['건강보험+요양'] = health_ins + care_ins
        
        deductions['소득세(지방세 포함)'] = total_income_tax + total_local_tax
        
        total_deduction = sum(deductions.values())

    net_pay = total_gross - total_deduction

    # -----------------------------------------------------------------------------
    # 5. 결과 출력
    # -----------------------------------------------------------------------------
    st.markdown(f"""
    <div class="result-box">
        <div style="font-size: 16px; color:#cccccc !important;">예상 실수령액</div>
        <div style="font-size: 32px; font-weight:bold; color:#0085ff !important; margin: 10px 0;">
            {int(net_pay):,} 원
        </div>
        <div style="border-top: 1px solid #555; padding-top: 10px;">
            <span style="font-size: 16px;">총 공제액: </span>
            <span style="font-size: 18px; font-weight:bold; color:#ff4b4b !important;">-{int(total_deduction):,} 원</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("") 
    
    if total_deduction > 0:
        with st.expander("🧾 공제 내역 자세히 보기"):
            for key, value in deductions.items():
                if value > 0:
                    st.markdown(f"**{key}:** {int(value):,} 원")
    
    st.write("")
