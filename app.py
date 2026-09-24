```python
import os
from datetime import datetime

import pandas as pd
import streamlit as st


# ============================================================
# CẤU HÌNH ỨNG DỤNG
# ============================================================

st.set_page_config(
    page_title="Order Nhà Hàng",
    page_icon="🍽️",
    layout="wide",
)

CSV_FILE = "history.csv"

# Mật khẩu Admin
ADMIN_PASSWORD = "123456"


# ============================================================
# THỰC ĐƠN NHÀ HÀNG
# ============================================================

MENU = {
    "🍔 Đồ ăn": {
        "Pizza Hải Sản": 150000,
        "Mì Ý Bò Bằm": 95000,
        "Burger Gà": 65000,
        "Salad Trộn": 50000,
        "Bít tết Bò Mỹ": 250000,
        "Sườn nướng BBQ": 180000,
        "Cánh gà chiên mắm": 75000,
        "Lẩu cá diêu hồng": 200000,
        "Lẩu Thái hải sản": 300000,
    },
    "🥤 Thức uống": {
        "Coca Cola": 20000,
        "Trà Đào Cam Sả": 35000,
        "Cà Phê Sữa": 25000,
        "Nước Suối": 10000,
        "Sinh tố Bơ": 45000,
        "Nước ép cam": 40000,
        "Mojito chanh dây": 55000,
        "Bia Heineken": 30000,
    },
}


# ============================================================
# KHỞI TẠO SESSION STATE
# ============================================================

if "order_dict" not in st.session_state:
    st.session_state.order_dict = {}

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# ============================================================
# HÀM ĐỌC LỊCH SỬ
# ============================================================

def load_history():
    """Đọc lịch sử giao dịch từ file CSV."""

    if not os.path.exists(CSV_FILE):
        return pd.DataFrame(
            columns=[
                "Mã đơn",
                "Thời gian",
                "Bàn",
                "Tên món",
                "Đơn giá",
                "Số lượng",
                "Thành tiền",
            ]
        )

    try:
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig")

        # Đảm bảo các cột tồn tại
        required_columns = [
            "Mã đơn",
            "Thời gian",
            "Bàn",
            "Tên món",
            "Đơn giá",
            "Số lượng",
            "Thành tiền",
        ]

        for column in required_columns:
            if column not in df.columns:
                df[column] = None

        return df[required_columns]

    except Exception:
        return pd.DataFrame(
            columns=[
                "Mã đơn",
                "Thời gian",
                "Bàn",
                "Tên món",
                "Đơn giá",
                "Số lượng",
                "Thành tiền",
            ]
        )


def save_history(df):
    """Lưu lịch sử giao dịch xuống CSV."""

    try:
        df.to_csv(
            CSV_FILE,
            index=False,
            encoding="utf-8-sig",
        )
        return True

    except Exception as e:
        st.error(f"Không thể lưu dữ liệu: {e}")
        return False


# ============================================================
# HÀM FORMAT TIỀN
# ============================================================

def format_money(value):
    return f"{value:,.0f} VNĐ"


# ============================================================
# HÀM TÍNH GIỎ HÀNG
# ============================================================

def calculate_cart():

    if not st.session_state.order_dict:
        return 0, 0, 0

    subtotal = sum(
        item["Thành tiền"]
        for item in st.session_state.order_dict.values()
    )

    discount = subtotal * 0.05 if subtotal > 1_000_000 else 0

    total = subtotal - discount

    return subtotal, discount, total


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🍽️ NHÀ HÀNG MR. BÌNH")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "📋 Chọn chức năng",
    [
        "🍽️ Order",
        "🔑 Admin",
    ],
)

st.sidebar.markdown("---")
st.sidebar.caption("Hệ thống quản lý Order & Doanh thu")
st.sidebar.caption("© Nhà hàng Mr. Bình")


# ============================================================
# TRANG ORDER
# ============================================================

if page == "🍽️ Order":

    st.title("🍽️ HỆ THỐNG ORDER NHÀ HÀNG")
    st.caption(
        "Ghi nhận món ăn, đồ uống và thanh toán nhanh chóng"
    )

    st.markdown("---")

    col_left, col_right = st.columns(
        [1, 1.5]
    )

    # ========================================================
    # KHU VỰC CHỌN MÓN
    # ========================================================

    with col_left:

        st.subheader("📝 Chọn món")

        table_number = st.selectbox(
            "🪑 Chọn số bàn",
            [f"Bàn {i}" for i in range(1, 21)],
        )

        category = st.selectbox(
            "📂 Loại món",
            list(MENU.keys()),
        )

        item = st.selectbox(
            "🍴 Chọn món",
            list(MENU[category].keys()),
        )

        price = MENU[category][item]

        st.info(
            f"Đơn giá: **{format_money(price)}**"
        )

        quantity = st.number_input(
            "🔢 Số lượng",
            min_value=1,
            max_value=100,
            value=1,
            step=1,
        )

        if st.button(
            "➕ Thêm vào giỏ",
            use_container_width=True,
            type="primary",
        ):

            if item in st.session_state.order_dict:

                st.session_state.order_dict[item]["Số lượng"] += quantity

                st.session_state.order_dict[item]["Thành tiền"] = (
                    st.session_state.order_dict[item]["Số lượng"]
                    * price
                )

                st.session_state.order_dict[item]["Bàn"] = table_number

            else:

                st.session_state.order_dict[item] = {
                    "Bàn": table_number,
                    "Tên món": item,
                    "Đơn giá": price,
                    "Số lượng": quantity,
                    "Thành tiền": price * quantity,
                }

            st.success(
                f"Đã thêm {item} vào giỏ hàng!"
            )

            st.rerun()

    # ========================================================
    # KHU VỰC GIỎ HÀNG
    # ========================================================

    with col_right:

        st.subheader("🛒 Giỏ hàng")

        if st.session_state.order_dict:

            df_cart = pd.DataFrame(
                list(st.session_state.order_dict.values())
            )

            st.dataframe(
                df_cart[
                    [
                        "Bàn",
                        "Tên món",
                        "Đơn giá",
                        "Số lượng",
                        "Thành tiền",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Đơn giá": st.column_config.NumberColumn(
                        "Đơn giá",
                        format="%d VNĐ",
                    ),
                    "Thành tiền": st.column_config.NumberColumn(
                        "Thành tiền",
                        format="%d VNĐ",
                    ),
                },
            )

            subtotal, discount, total = calculate_cart()

            st.markdown("---")

            money_col1, money_col2, money_col3 = st.columns(3)

            with money_col1:
                st.metric(
                    "Tạm tính",
                    format_money(subtotal),
                )

            with money_col2:
                st.metric(
                    "Giảm giá",
                    format_money(discount),
                )

            with money_col3:
                st.metric(
                    "Thanh toán",
                    format_money(total),
                )

            if discount > 0:

                st.success(
                    "🎉 Hóa đơn trên 1.000.000 VNĐ được giảm 5%!"
                )

            st.markdown("---")

            btn1, btn2 = st.columns(2)

            # =================================================
            # THANH TOÁN
            # =================================================

            with btn1:

                if st.button(
                    "💳 Thanh toán",
                    use_container_width=True,
                    type="primary",
                ):

                    now = datetime.now()

                    time_string = now.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    order_id = now.strftime(
                        "HD%Y%m%d%H%M%S"
                    )

                    df_history = load_history()

                    new_rows = []

                    for row in st.session_state.order_dict.values():

                        new_rows.append(
                            {
                                "Mã đơn": order_id,
                                "Thời gian": time_string,
                                "Bàn": row["Bàn"],
                                "Tên món": row["Tên món"],
                                "Đơn giá": row["Đơn giá"],
                                "Số lượng": row["Số lượng"],
                                "Thành tiền": row["Thành tiền"],
                            }
                        )

                    new_df = pd.DataFrame(new_rows)

                    df_history = pd.concat(
                        [
                            df_history,
                            new_df,
                        ],
                        ignore_index=True,
                    )

                    if save_history(df_history):

                        st.success(
                            f"✅ Thanh toán thành công! Mã hóa đơn: {order_id}"
                        )

                        st.session_state.order_dict = {}

                        st.rerun()

            # =================================================
            # XÓA GIỎ
            # =================================================

            with btn2:

                if st.button(
                    "🗑️ Xóa toàn bộ giỏ",
                    use_container_width=True,
                ):

                    st.session_state.order_dict = {}

                    st.rerun()

        else:

            st.info(
                "🛒 Giỏ hàng đang trống. "
                "Hãy chọn món ở bên trái."
            )


# ============================================================
# TRANG ADMIN
# ============================================================

elif page == "🔑 Admin":

    st.title("🔑 QUẢN TRỊ HỆ THỐNG")

    # ========================================================
    # ĐĂNG NHẬP ADMIN
    # ========================================================

    if not st.session_state.admin_logged_in:

        st.subheader("🔐 Đăng nhập quản trị")

        with st.form("admin_login"):

            password = st.text_input(
                "Mật khẩu",
                type="password",
            )

            login = st.form_submit_button(
                "🔑 Đăng nhập",
                use_container_width=True,
            )

            if login:

                if password == ADMIN_PASSWORD:

                    st.session_state.admin_logged_in = True

                    st.success(
                        "Đăng nhập thành công!"
                    )

                    st.rerun()

                else:

                    st.error(
                        "❌ Mật khẩu không chính xác!"
                    )

        st.warning(
            "Chỉ tài khoản quản trị mới có thể xem dữ liệu doanh thu."
        )

        st.stop()

    # ========================================================
    # HEADER ADMIN
    # ========================================================

    header1, header2 = st.columns(
        [4, 1]
    )

    with header1:

        st.success(
            "🟢 Đã xác thực quyền quản trị viên"
        )

    with header2:

        if st.button(
            "🔒 Đăng xuất",
            use_container_width=True,
        ):

            st.session_state.admin_logged_in = False

            st.rerun()

    # ========================================================
    # ĐỌC DỮ LIỆU
    # ========================================================

    df_history = load_history()

    # ========================================================
    # TABS ADMIN
    # ========================================================

    tab_menu, tab_revenue, tab_analysis = st.tabs(
        [
            "📋 Thực đơn",
            "💰 Doanh thu",
            "📊 Phân tích",
        ]
    )


    # ========================================================
    # TAB 1 - MENU
    # ========================================================

    with tab_menu:

        st.subheader(
            "🍴 Danh sách thực đơn hiện tại"
        )

        menu_data = []

        for category_name, items in MENU.items():

            for item_name, item_price in items.items():

                menu_data.append(
                    {
                        "Phân loại": category_name,
                        "Tên món": item_name,
                        "Đơn giá": item_price,
                    }
                )

        df_menu = pd.DataFrame(menu_data)

        st.dataframe(
            df_menu,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Đơn giá": st.column_config.NumberColumn(
                    "Đơn giá",
                    format="%d VNĐ",
                )
            },
        )


    # ========================================================
    # TAB 2 - DOANH THU
    # ========================================================

    with tab_revenue:

        st.subheader(
            "💰 Doanh thu & lịch sử thanh toán"
        )

        if not df_history.empty:

            # Đảm bảo kiểu dữ liệu số
            df_history["Số lượng"] = pd.to_numeric(
                df_history["Số lượng"],
                errors="coerce",
            ).fillna(0)

            df_history["Thành tiền"] = pd.to_numeric(
                df_history["Thành tiền"],
                errors="coerce",
            ).fillna(0)

            total_revenue = df_history[
                "Thành tiền"
            ].sum()

            total_quantity = df_history[
                "Số lượng"
            ].sum()

            total_orders = df_history[
                "Mã đơn"
            ].nunique()

            # ================================================
            # KPI
            # ================================================

            kpi1, kpi2, kpi3 = st.columns(3)

            with kpi1:

                st.metric(
                    "💰 Tổng doanh thu",
                    format_money(total_revenue),
                )

            with kpi2:

                st.metric(
                    "🍽️ Tổng món đã bán",
                    f"{int(total_quantity):,} phần",
                )

            with kpi3:

                st.metric(
                    "🧾 Số hóa đơn",
                    f"{total_orders:,}",
                )

            st.markdown("---")

            # ================================================
            # DOANH THU THEO NGÀY
            # ================================================

            st.subheader(
                "📅 Doanh thu theo ngày"
            )

            df_history["Thời gian"] = pd.to_datetime(
                df_history["Thời gian"],
                errors="coerce",
            )

            df_history["Ngày"] = (
                df_history["Thời gian"]
                .dt.date
            )

            daily = (
                df_history
                .groupby("Ngày")["Thành tiền"]
                .sum()
                .reset_index()
            )

            daily.columns = [
                "Ngày",
                "Doanh thu",
            ]

            chart_col, table_col = st.columns(
                [1.5, 1]
            )

            with chart_col:

                st.bar_chart(
                    daily.set_index("Ngày")[
                        "Doanh thu"
                    ]
                )

            with table_col:

                st.dataframe(
                    daily.style.format(
                        {
                            "Doanh thu":
                                "{:,.0f} VNĐ"
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            st.markdown("---")

            # ================================================
            # LỊCH SỬ GIAO DỊCH
            # ================================================

            st.subheader(
                "🧾 Chi tiết lịch sử thanh toán"
            )

            st.dataframe(
                df_history[
                    [
                        "Mã đơn",
                        "Thời gian",
                        "Bàn",
                        "Tên món",
                        "Đơn giá",
                        "Số lượng",
                        "Thành tiền",
                    ]
                ].sort_values(
                    "Thời gian",
                    ascending=False,
                ),
                use_container_width=True,
                hide_index=True,
            )

            # ================================================
            # DOWNLOAD CSV
            # ================================================

            csv_data = df_history.to_csv(
                index=False,
                encoding="utf-8-sig",
            )

            st.download_button(
                "📥 Tải lịch sử giao dịch",
                data=csv_data,
                file_name="history_backup.csv",
                mime="text/csv",
                use_container_width=True,
            )

        else:

            st.info(
                "Chưa có giao dịch nào được ghi nhận."
            )


    # ========================================================
    # TAB 3 - PHÂN TÍCH
    # ========================================================

    with tab_analysis:

        st.subheader(
            "📊 Phân tích bán hàng"
        )

        if not df_history.empty:

            df_anal = df_history.copy()

            df_anal["Thời gian"] = pd.to_datetime(
                df_anal["Thời gian"],
                errors="coerce",
            )

            df_anal["Số lượng"] = pd.to_numeric(
                df_anal["Số lượng"],
                errors="coerce",
            ).fillna(0)

            df_anal["Thành tiền"] = pd.to_numeric(
                df_anal["Thành tiền"],
                errors="coerce",
            ).fillna(0)

            df_anal["Giờ"] = (
                df_anal["Thời gian"].dt.hour
            )

            df_anal["Tháng"] = (
                df_anal["Thời gian"]
                .dt.strftime("%m/%Y")
            )

            # ================================================
            # MÓN BÁN CHẠY NHẤT
            # ================================================

            item_sales = (
                df_anal
                .groupby("Tên món")["Số lượng"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            best_seller = item_sales.index[0]

            best_seller_quantity = item_sales.iloc[0]

            # ================================================
            # KHUNG GIỜ BÁN CHẠY
            # ================================================

            hourly_sales = (
                df_anal
                .groupby("Giờ")["Số lượng"]
                .sum()
            )

            best_hour = hourly_sales.idxmax()

            best_hour_quantity = hourly_sales.max()

            # ================================================
            # THÁNG DOANH THU CAO NHẤT
            # ================================================

            monthly_revenue = (
                df_anal
                .groupby("Tháng")["Thành tiền"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            best_month = monthly_revenue.index[0]

            best_month_revenue = monthly_revenue.iloc[0]

            # ================================================
            # KPI
            # ================================================

            kpi1, kpi2, kpi3 = st.columns(3)

            with kpi1:

                st.info(
                    "🏆 MÓN BÁN CHẠY NHẤT"
                )

                st.metric(
                    best_seller,
                    f"{int(best_seller_quantity)} phần",
                )

            with kpi2:

                st.warning(
                    "⏰ KHUNG GIỜ BÁN CHẠY"
                )

                st.metric(
                    f"{best_hour:02d}:00 - "
                    f"{(best_hour + 1) % 24:02d}:00",
                    f"{int(best_hour_quantity)} phần",
                )

            with kpi3:

                st.success(
                    "📅 THÁNG DOANH THU CAO"
                )

                st.metric(
                    best_month,
                    format_money(
                        best_month_revenue
                    ),
                )

            st.markdown("---")

            # ================================================
            # PHÂN TÍCH MÓN ĂN
            # ================================================

            st.subheader(
                "🍔 Doanh thu & số lượng từng món"
            )

            item_summary = (
                df_anal
                .groupby("Tên món")
                .agg(
                    Số_lượng_bán=(
                        "Số lượng",
                        "sum",
                    ),
                    Doanh_thu=(
                        "Thành tiền",
                        "sum",
                    ),
                )
                .reset_index()
                .sort_values(
                    "Số_lượng_bán",
                    ascending=False,
                )
            )

            chart1, table1 = st.columns(
                [1.5, 1]
            )

            with chart1:

                st.bar_chart(
                    item_summary.set_index(
                        "Tên món"
                    )["Số_lượng_bán"]
                )

            with table1:

                st.dataframe(
                    item_summary.style.format(
                        {
                            "Doanh_thu":
                                "{:,.0f} VNĐ"
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            st.markdown("---")

            # ================================================
            # PHÂN TÍCH KHUNG GIỜ
            # ================================================

            st.subheader(
                "⏰ Phân tích bán hàng theo giờ"
            )

            hourly_summary = (
                df_anal
                .groupby("Giờ")
                .agg(
                    Số_lượng_món=(
                        "Số lượng",
                        "sum",
                    ),
                    Doanh_thu=(
                        "Thành tiền",
                        "sum",
                    ),
                )
                .reset_index()
            )

            all_hours = pd.DataFrame(
                {
                    "Giờ": range(24)
                }
            )

            hourly_summary = pd.merge(
                all_hours,
                hourly_summary,
                on="Giờ",
                how="left",
            ).fillna(0)

            chart2, table2 = st.columns(
                [1.5, 1]
            )

            with chart2:

                st.bar_chart(
                    hourly_summary.set_index(
                        "Giờ"
                    )["Số_lượng_món"]
                )

            with table2:

                st.dataframe(
                    hourly_summary[
                        hourly_summary[
                            "Số_lượng_món"
                        ] > 0
                    ].style.format(
                        {
                            "Doanh_thu":
                                "{:,.0f} VNĐ"
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            st.info(
                f"⏰ Khung giờ có số lượng món "
                f"được thanh toán cao nhất là "
                f"**{best_hour:02d}:00 - "
                f"{(best_hour + 1) % 24:02d}:00**, "
                f"với **{int(best_hour_quantity)} phần**."
            )

            st.markdown("---")

            # ================================================
            # DOANH THU THEO THÁNG
            # ================================================

            st.subheader(
                "📅 Doanh thu theo tháng"
            )

            monthly_summary = (
                df_anal
                .groupby("Tháng")
                .agg(
                    Số_lượng_bán=(
                        "Số lượng",
                        "sum",
                    ),
                    Doanh_thu=(
                        "Thành tiền",
                        "sum",
                    ),
                )
                .reset_index()
            )

            chart3, table3 = st.columns(
                [1.5, 1]
            )

            with chart3:

                st.bar_chart(
                    monthly_summary.set_index(
                        "Tháng"
                    )["Doanh_thu"]
                )

            with table3:

                st.dataframe(
                    monthly_summary.style.format(
                        {
                            "Doanh_thu":
                                "{:,.0f} VNĐ"
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

        else:

            st.info(
                "📭 Chưa có dữ liệu giao dịch. "
                "Hãy thanh toán một vài đơn hàng "
                "để hệ thống bắt đầu phân tích."
            )
```

