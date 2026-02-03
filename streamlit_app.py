import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. 페이지 설정 및 디자인 (다크 & 네온 블루 테마)
# -----------------------------------------------------------------------------
st.set_page_config(page_title="건설 일용직 실수령액 계산기", page_icon="🏗️")

# 커스텀 CSS (BuildTech 스타일)
hide_st_style = """
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
            
            /* 1. 글로벌 폰트 & 색상 강제 통일 */
            html, body, [class*="css"]  {
                font-family: 'Noto Sans KR', sans-serif;
                color: #ffffff !important;
            }
            
            /* 2. 메인 배경 */
            .stApp {
                background-color: #1a1a1a;
            }
            
            /* 3. 입력창 스타일 */
            .stNumberInput input {
                background-color: #333333 !important;
                color: #ffffff !important;
                font-weight: bold;
                border: 1px solid #555555;
            }
            
            /* 4. 각종 라벨 & 선택지 글씨 */
            .stNumberInput label, .stRadio label, .stCheckbox label {
                color: #ffffff !important;
                font-weight: bold;
            }
            .stRadio p, .stCheckbox p { /* 라디오 버튼 옆 글씨 */
                color: #ffffff !important;
            }

            /* ★★★ 5. 결과 박스 내부 글씨 (여기가 핵심!) ★★★ */
            .result-box p, .result-box span {
                color: #ffffff !important; /* 무조건 흰색 */
            }
            .sub-text {
                color: #dddddd !important; /* 살짝 연한 흰색 */
            }
            
            /* ★★★ 6. "자세히 보기" (Expander) 내부 글씨 ★★★ */
            .streamlit-expanderHeader {
                color: #ffffff !important;
                background-color: #333333 !important; /* 헤더 배경도 살짝 밝게 */
            }
            .streamlit-expanderContent p, .streamlit-expanderContent div {
                color: #cccccc !important; /* 내부는 가독성 위해 살짝 밝은 회색 */
            }
            
            /* 7. 맨 아래 '참고' 박스 (Info Box) */
            .stAlert {
                background-color: #222222 !important;
                color: #ffffff !important;
            }
            
            /* 8. 버튼 스타일 */
            div.stButton > button {
                background-color: #0085ff;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
                width: 100%;
                padding: 12px;
                margin-top: 10px;
            }
            div.stButton > button:hover {
                background-color: #0066cc;
                border: 2px solid #ffffff;
            }
            
            /* 9. 불필요 요소 숨김 */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            /* 10. 결과 박스 디자인 */
            .result-box {
                background-color: #262626;
                padding: 20px;
                border-radius: 10px;
                border-left: 5px solid #0085ff;
                margin-top: 20px;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. 타이틀 영역
# -----------------------------------------------------------------------------
st.markdown("<h2 style='text-align: center; color: #ffffff;'>🏗️ 일용직 실수령액 계산기</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #aaaaaa;'>오늘의 땀방울이 얼마가 되는지 확인해보세요.</p>", unsafe_allow_html=True)
st.write("---")

# -----------------------------------------------------------------------------
# 3. 입력 영역 (UI)
# -----------------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    daily_wage = st.number_input("일당 (원)", value=180000, step=10000, format="%d")

with col2:
    work_days = st.number_input("출력 공수 (일)", value=20.0, step=0.5, format="%.1f")

# 공제 방식 선택
calc_type = st.radio(
    "공제 방식 선택",
    ("일반 건설 일용직 (4대보험+세금)", "3.3% 공제 (프리랜서/인력사무소)"),
    horizontal=True
)

# 8일 이상 근무 여부 (일반 일용직일 때만 표시)
if calc_type == "일반 건설 일용직 (4대보험+세금)":
    apply_insurance = st.checkbox("월 8일 이상 근무 (국민/건강보험 적용)", value=True)
else:
    apply_insurance = False

# -----------------------------------------------------------------------------
# 4. 계산 로직 (2025/2026 기준 요율 적용)
# -----------------------------------------------------------------------------
if st.button("계산하기 💸"):
    total_gross = daily_wage * work_days # 총 급여(세전)
    deductions = {} # 공제 항목 저장
    
    total_deduction = 0
    
    if calc_type == "3.3% 공제 (프리랜서/인력사무소)":
        # 단순 3.3% 계산
        tax = total_gross * 0.033
        deductions['사업소득세(3.3%)'] = tax
        total_deduction = tax
        
    else: # 일반 건설 일용직
        # A. 소득세 (일당 15만원 비과세)
        # 공식: (일당 - 150,000) * 6% * 45%(55%감면) * 일수 * 1.1(지방세포함) = 약 2.97%
        # 간단 계산을 위해: 과세대상 * 2.7% (소득세) + 소득세의 10% (지방세)
        
        taxable_daily = max(0, daily_wage - 150000)
        daily_income_tax = taxable_daily * 0.06 * 0.45
        daily_local_tax = daily_income_tax * 0.1
        
        total_income_tax = int(daily_income_tax * work_days) # 원단위 절사 생략하고 단순화
        total_local_tax = int(daily_local_tax * work_days)
        
        # B. 4대 보험 (근로자 부담분) - 2025년 예상 요율 반영
        # 고용보험: 0.9% (실업급여)
        emp_ins = int(total_gross * 0.009)
        
        health_ins = 0
        care_ins = 0
        pension_ins = 0
        
        if apply_insurance: # 8일 이상 시 적용
            # 국민연금: 4.5% (상한액 고려 안함, 단순계산)
            pension_ins = int(total_gross * 0.045)
            # 건강보험: 약 3.545%
            health_ins = int(total_gross * 0.03545)
            # 장기요양: 건강보험료의 약 12.95%
            care_ins = int(health_ins * 0.1295)
            
        # 합산
        deductions['고용보험(0.9%)'] = emp_ins
        if apply_insurance:
            deductions['국민연금(4.5%)'] = pension_ins
            deductions['건강보험+요양'] = health_ins + care_ins
        
        deductions['소득세(지방세 포함)'] = total_income_tax + total_local_tax
        
        total_deduction = sum(deductions.values())

    # 최종 실수령액
    net_pay = total_gross - total_deduction

    # -----------------------------------------------------------------------------
    # 5. 결과 출력
    # -----------------------------------------------------------------------------
    st.markdown(f"""
    <div class="result-box">
        <p class="sub-text">예상 실수령액</p>
        <p class="big-font">{int(net_pay):,} 원</p>
        <p style='color:white; font-size:14px;'>총 공제액: <span style='color:#ff4b4b;'>-{int(total_deduction):,} 원</span></p>
    </div>
    """, unsafe_allow_html=True)

    st.write("") # 여백
    
    # 상세 내역 (데이터프레임 or 텍스트)
    if total_deduction > 0:
        with st.expander("🧾 공제 내역 자세히 보기 (클릭)", expanded=True):
            for key, value in deductions.items():
                if value > 0:
                    st.markdown(f"**{key}:** {int(value):,} 원")
    
    st.info("💡 참고: 실제 지급액은 회사 규정, 갑근세 적용 방식, 공제회비 유무에 따라 차이가 있을 수 있습니다.")
