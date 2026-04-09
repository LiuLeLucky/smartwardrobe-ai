"""
SmartWardrobe AI — Streamlit prototype UI
Run: streamlit run app/ui.py
Backend must be running at BASE_URL.
"""
import streamlit as st
import requests
from datetime import datetime

# ── constants ────────────────────────────────────────────────────────────────

BASE_URL = "http://127.0.0.1:8001"

OCCASIONS   = ["Casual", "Formal", "Sport", "Date", "Work"]
STYLES      = ["Minimalist", "Vintage", "Streetwear", "Professional"]
CATEGORIES  = ["Top", "Bottom", "Shoes", "Outerwear", "Accessory"]
SEASONS     = ["spring", "summer", "autumn", "winter"]

SCORE_COLOR = {"A": "#27ae60", "B": "#e67e22", "C": "#e74c3c"}
SCORE_LABEL = {"A": "Perfect", "B": "Good",    "C": "Fair"}

PAGES = ["Login", "My Wardrobe", "Create Outfit", "Generate Outfit", "My Outfits"]


# ── API helpers ───────────────────────────────────────────────────────────────

def _headers() -> dict:
    token = st.session_state.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _check_auth(resp: requests.Response) -> bool:
    """Return True if OK, handle 401 by clearing session and returning False."""
    if resp.status_code == 401:
        st.session_state["token"] = None
        st.session_state["page"]  = "Login"
        st.error("Session expired — please log in again.")
        st.rerun()
    return resp.status_code not in (401,)


# ── shared components ─────────────────────────────────────────────────────────

def _score_badge(score: str | None) -> str:
    if not score:
        return ""
    color = SCORE_COLOR.get(score, "#888")
    label = SCORE_LABEL.get(score, score)
    return (
        f'<span style="background:{color};color:#fff;padding:2px 10px;'
        f'border-radius:12px;font-weight:700;font-size:0.85rem;">'
        f'{score} · {label}</span>'
    )


def _color_swatch(hex_code: str) -> str:
    return (
        f'<span style="display:inline-block;width:18px;height:18px;'
        f'background:{hex_code};border:1px solid #ccc;border-radius:3px;'
        f'vertical-align:middle;margin-right:6px;"></span>'
        f'<code>{hex_code}</code>'
    )


def _season_tags(seasons: list) -> str:
    colors = {"spring": "#a8d8a8", "summer": "#ffd580",
              "autumn": "#f4a460", "winter": "#aed6f1"}
    tags = []
    for s in seasons:
        bg = colors.get(s, "#ddd")
        tags.append(
            f'<span style="background:{bg};padding:1px 8px;border-radius:10px;'
            f'font-size:0.78rem;margin-right:3px;">{s}</span>'
        )
    return "".join(tags)


def _fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).strftime("%b %d, %Y")
    except Exception:
        return iso


def render_clothing_card(
    item: dict,
    show_delete: bool = False,
    show_edit: bool = False,
    key_prefix: str = "",
) -> bool:
    """
    Render one clothing item card.
    Returns True if the delete button was confirmed for this item.
    Edit is handled entirely inside this function via session_state.
    """
    iid = item["id"]
    confirm_key = f"del_confirm_{key_prefix}{iid}"
    editing = show_edit and st.session_state.get("editing_item_id") == iid

    with st.container(border=True):
        # Image (if available) — fetch bytes explicitly so failures are not silent
        if item.get("image_url"):
            try:
                img_resp = requests.get(BASE_URL + item["image_url"], timeout=4)
                if img_resp.status_code == 200:
                    st.image(img_resp.content, use_container_width=True)
                else:
                    st.caption(f"(image {img_resp.status_code})")
            except requests.exceptions.RequestException:
                st.caption("(image unavailable)")

        st.markdown(f"**{item['sub_category']}**")
        st.caption(item["category"])
        st.markdown(_color_swatch(item["color_code"]), unsafe_allow_html=True)
        st.markdown(f"*{item['material']}*")
        st.markdown(_season_tags(item.get("season", [])), unsafe_allow_html=True)

        # ── Action buttons ────────────────────────────────────────────────────
        if show_delete and st.session_state.get(confirm_key):
            # Delete confirmation flow (full width)
            st.warning("Confirm delete?")
            col_y, col_n = st.columns(2)
            if col_y.button("Yes, delete", key=f"del_yes_{key_prefix}{iid}", type="primary"):
                st.session_state.pop(confirm_key, None)
                return True
            if col_n.button("Cancel", key=f"del_no_{key_prefix}{iid}"):
                st.session_state[confirm_key] = False
                st.rerun()
        else:
            # Normal state: Edit and/or Delete side by side
            num_btns = int(show_edit) + int(show_delete)
            if num_btns == 2:
                col_e, col_d = st.columns(2)
            elif show_edit:
                col_e = st.columns(1)[0]
            elif show_delete:
                col_d = st.columns(1)[0]

            if show_edit:
                label = "Cancel edit" if editing else "Edit"
                if col_e.button(label, key=f"edit_btn_{key_prefix}{iid}"):
                    if editing:
                        st.session_state.pop("editing_item_id", None)
                    else:
                        st.session_state["editing_item_id"] = iid
                    st.rerun()

            if show_delete:
                if col_d.button("Delete", key=f"del_btn_{key_prefix}{iid}"):
                    st.session_state[confirm_key] = True
                    st.rerun()

        # ── Inline edit form (shown only for the item being edited) ──────────
        if editing:
            with st.expander("Edit item", expanded=True):
                cur_cat_idx = CATEGORIES.index(item["category"]) if item["category"] in CATEGORIES else 0
                cur_seasons = [s for s in item.get("season", []) if s in SEASONS]

                with st.form(key=f"edit_form_{key_prefix}{iid}"):
                    e_category = st.selectbox("Category", CATEGORIES, index=cur_cat_idx)
                    e_sub_cat  = st.text_input("Sub-category", value=item["sub_category"])
                    e_color    = st.color_picker("Color", value=item["color_code"])
                    e_material = st.text_input("Material", value=item["material"])
                    e_season   = st.multiselect("Season", SEASONS, default=cur_seasons)

                    save_col, cancel_col = st.columns(2)
                    save_btn   = save_col.form_submit_button("Save changes", type="primary")
                    cancel_btn = cancel_col.form_submit_button("Cancel")

                if save_btn:
                    patch_resp = requests.patch(
                        f"{BASE_URL}/clothing/{iid}",
                        json={
                            "category":     e_category,
                            "sub_category": e_sub_cat,
                            "color_code":   e_color.upper(),
                            "material":     e_material,
                            "season":       e_season,
                        },
                        headers=_headers(),
                        timeout=8,
                    )
                    if patch_resp.status_code == 200:
                        st.success("Updated successfully!")
                        st.session_state.pop("editing_item_id", None)
                        st.rerun()
                    else:
                        detail = patch_resp.json().get("detail", "unknown error")
                        st.error(f"Update failed: {detail}")

                if cancel_btn:
                    st.session_state.pop("editing_item_id", None)
                    st.rerun()

    return False


# ── Page 1 — Login / Register ─────────────────────────────────────────────────

def page_login():
    st.title("SmartWardrobe AI")
    st.subheader("Welcome — please log in or create an account")

    tab_login, tab_reg = st.tabs(["Login", "Register"])

    # ── Login tab ──
    with tab_login:
        with st.form("login_form"):
            email    = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit   = st.form_submit_button("Log in", type="primary")

        if submit:
            if not email or not password:
                st.error("Please enter both email and password.")
            else:
                try:
                    resp = requests.post(
                        f"{BASE_URL}/auth/login",
                        data={"username": email, "password": password},
                        timeout=8,
                    )
                    if resp.status_code == 200:
                        st.session_state["token"] = resp.json()["access_token"]
                        st.session_state["page"]  = "My Wardrobe"
                        st.success("Logged in!")
                        st.rerun()
                    else:
                        detail = resp.json().get("detail", "Login failed.")
                        st.error(f"Login failed: {detail}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot reach the API at {BASE_URL}. Is the backend running?")

    # ── Register tab ──
    with tab_reg:
        with st.form("register_form"):
            reg_email    = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_pw")
            reg_submit   = st.form_submit_button("Create account", type="primary")

        if reg_submit:
            if not reg_email or not reg_password:
                st.error("Please fill in both fields.")
            elif len(reg_password) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    resp = requests.post(
                        f"{BASE_URL}/auth/register",
                        json={"email": reg_email, "password": reg_password},
                        timeout=8,
                    )
                    if resp.status_code == 201:
                        st.success("Account created! Please log in.")
                    else:
                        detail = resp.json().get("detail", "Registration failed.")
                        st.error(f"Registration failed: {detail}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot reach the API at {BASE_URL}. Is the backend running?")


# ── Page 2 — My Wardrobe ──────────────────────────────────────────────────────

def page_wardrobe():
    st.title("My Wardrobe")

    # ── Sidebar: Add new item ──
    with st.sidebar:
        st.header("Add a clothing item")
        with st.form("add_clothing_form", clear_on_submit=True):
            category    = st.selectbox("Category", CATEGORIES)
            sub_cat     = st.text_input("Sub-category (e.g. 'White Shirt')")
            color_hex   = st.color_picker("Color", value="#FFFFFF")
            material    = st.text_input("Material (e.g. 'Cotton')")
            season_sel  = st.multiselect("Season", SEASONS, default=[])
            img_file    = st.file_uploader(
                "Photo (optional)", type=["jpg", "jpeg", "png", "webp"]
            )
            add_submit  = st.form_submit_button("Add item", type="primary")

        if add_submit:
            has_image = img_file is not None

            # Without an image, all fields must be filled in manually
            if not has_image and (not sub_cat or not material or not season_sel):
                st.sidebar.error("Sub-category, material, and at least one season are required.")
            else:
                payload = {
                    "category":     category,
                    "sub_category": sub_cat or "Unknown",
                    "color_code":   color_hex.upper(),
                    "material":     material or "Unknown",
                    "season":       season_sel if season_sel else [],
                }
                resp = requests.post(
                    f"{BASE_URL}/clothing/",
                    json=payload,
                    headers=_headers(),
                    timeout=8,
                )
                if not _check_auth(resp):
                    return
                if resp.status_code == 201:
                    new_item = resp.json()
                    if has_image:
                        with st.spinner("Analyzing your clothing with AI..."):
                            up = requests.post(
                                f"{BASE_URL}/clothing/{new_item['id']}/upload-image",
                                files={"file": (img_file.name, img_file.getvalue(), img_file.type)},
                                headers=_headers(),
                                timeout=60,
                            )
                        if up.status_code != 200:
                            st.sidebar.warning(
                                "Item added but image upload failed: "
                                + up.json().get("detail", "unknown error")
                            )
                        else:
                            tagged = up.json()
                            display_name = tagged.get("sub_category") or sub_cat or "Item"
                            st.sidebar.success(f"'{display_name}' added and tagged by AI!")
                    else:
                        st.sidebar.success(f"'{sub_cat}' added!")
                    st.rerun()
                else:
                    detail = resp.json().get("detail", "Could not add item.")
                    st.sidebar.error(f"Error: {detail}")

    # ── Main: fetch and display wardrobe ──
    try:
        resp = requests.get(f"{BASE_URL}/clothing/", headers=_headers(), timeout=8)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the API at {BASE_URL}.")
        return

    if not _check_auth(resp):
        return

    items = resp.json()

    if not items:
        st.info("Your wardrobe is empty. Use the sidebar to add your first item!")
        return

    st.caption(f"{len(items)} item{'s' if len(items) != 1 else ''} in your wardrobe")

    # 3-column grid
    cols = st.columns(3)
    for i, item in enumerate(items):
        with cols[i % 3]:
            if render_clothing_card(item, show_delete=True, show_edit=True, key_prefix="wrd_"):
                del_resp = requests.delete(
                    f"{BASE_URL}/clothing/{item['id']}",
                    headers=_headers(),
                    timeout=8,
                )
                if del_resp.status_code == 204:
                    st.success("Item deleted.")
                    st.rerun()
                else:
                    st.error("Delete failed: " + del_resp.json().get("detail", ""))


# ── Page 3 — Generate Outfit ──────────────────────────────────────────────────

def _render_outfit_preview(outfit: dict) -> None:
    """Render the outfit preview card (name, score, explanation, item cards)."""
    st.divider()
    head_col, badge_col = st.columns([4, 1])
    head_col.subheader(outfit.get("name", "Generated Outfit"))
    badge_col.markdown(_score_badge(outfit.get("ai_score")), unsafe_allow_html=True)

    if outfit.get("ai_explanation"):
        st.info(outfit["ai_explanation"])

    st.write(f"**Occasion:** {outfit.get('occasion', '—')}")

    st.write("**Selected items:**")
    clothing_items = outfit.get("clothing_items", [])
    if clothing_items:
        cols = st.columns(min(len(clothing_items), 3))
        for i, item in enumerate(clothing_items):
            with cols[i % 3]:
                render_clothing_card(item, show_delete=False, key_prefix="gen_")
    else:
        st.caption("No items returned.")


def page_generate():
    st.title("Generate Outfit")

    preview = st.session_state.get("preview_outfit")

    # ── Show Generate form only when no preview is pending ──
    if not preview:
        st.write("Let the AI pick an outfit from your wardrobe for any occasion.")

        with st.form("generate_form"):
            col1, col2 = st.columns(2)
            occasion   = col1.selectbox("Occasion", OCCASIONS)
            style_pref = col2.selectbox("Style preference", STYLES)
            gen_submit = st.form_submit_button("Generate", type="primary")

        if gen_submit:
            with st.spinner("Asking the AI stylist..."):
                try:
                    resp = requests.post(
                        f"{BASE_URL}/outfits/generate",
                        json={"occasion": occasion, "style_preference": style_pref},
                        headers=_headers(),
                        timeout=60,
                    )
                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot reach the API at {BASE_URL}.")
                    return

            if not _check_auth(resp):
                return

            if resp.status_code == 400:
                st.warning("Add at least 2 items to your wardrobe first.")
                return

            if resp.status_code == 503:
                st.error(
                    "The AI provider is unavailable: "
                    + resp.json().get("detail", "check your API key configuration.")
                )
                return

            if resp.status_code != 201:
                st.error(f"Unexpected error ({resp.status_code}): {resp.json().get('detail', '')}")
                return

            st.session_state["preview_outfit"] = resp.json()
            st.rerun()

    # ── Preview + Save / Discard ──
    else:
        st.info("Review your generated outfit, then save or discard it.")
        _render_outfit_preview(preview)

        st.divider()
        save_col, discard_col = st.columns(2)

        if save_col.button("Save Outfit", type="primary", use_container_width=True):
            save_resp = requests.post(
                f"{BASE_URL}/outfits/{preview['id']}/save",
                headers=_headers(),
                timeout=8,
            )
            if not _check_auth(save_resp):
                return
            if save_resp.status_code == 200:
                st.session_state.pop("preview_outfit", None)
                st.success("Outfit saved successfully!")
                st.rerun()
            else:
                st.error("Save failed: " + save_resp.json().get("detail", "unknown error"))

        if discard_col.button("Discard", use_container_width=True):
            del_resp = requests.delete(
                f"{BASE_URL}/outfits/{preview['id']}",
                headers=_headers(),
                timeout=8,
            )
            if not _check_auth(del_resp):
                return
            st.session_state.pop("preview_outfit", None)
            if del_resp.status_code == 204:
                st.info("Outfit discarded.")
            else:
                st.warning("Could not delete outfit from server, preview cleared.")
            st.rerun()


# ── Page 4 — My Outfits ───────────────────────────────────────────────────────

def _render_outfit_list(outfits: list, tab_key: str) -> None:
    """Render a list of outfit cards with a Delete button each."""
    for outfit in outfits:
        oid = outfit["id"]
        with st.container(border=True):
            h_col, b_col, d_col = st.columns([5, 2, 2])
            h_col.markdown(f"### {outfit.get('name', 'Outfit')}")
            b_col.markdown(_score_badge(outfit.get("ai_score")), unsafe_allow_html=True)
            d_col.caption(_fmt_date(outfit.get("created_at", "")))

            if outfit.get("occasion"):
                st.write(f"**Occasion:** {outfit['occasion']}")

            if outfit.get("ai_explanation"):
                st.info(outfit["ai_explanation"])

            items = outfit.get("clothing_items", [])
            if items:
                st.write("**Items in this outfit:**")
                item_cols = st.columns(min(len(items), 4))
                for i, item in enumerate(items):
                    with item_cols[i % 4]:
                        render_clothing_card(item, show_delete=False, key_prefix=f"{tab_key}_{oid}_")

            if st.button("Delete", key=f"del_outfit_{tab_key}_{oid}"):
                del_resp = requests.delete(
                    f"{BASE_URL}/outfits/{oid}",
                    headers=_headers(),
                    timeout=8,
                )
                if del_resp.status_code == 204:
                    st.success("Outfit deleted.")
                    st.rerun()
                else:
                    st.error("Delete failed: " + del_resp.json().get("detail", "unknown error"))

        st.write("")  # vertical spacer


def page_outfits():
    st.title("My Outfits")

    try:
        resp = requests.get(f"{BASE_URL}/outfits/", headers=_headers(), timeout=8)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the API at {BASE_URL}.")
        return

    if not _check_auth(resp):
        return

    # Filter to saved outfits only, newest first
    all_outfits = sorted(
        [o for o in resp.json() if o.get("is_saved")],
        key=lambda o: o.get("created_at", ""),
        reverse=True,
    )

    ai_outfits     = [o for o in all_outfits if o.get("source") == "ai"]
    manual_outfits = [o for o in all_outfits if o.get("source") == "manual"]

    tab_ai, tab_manual = st.tabs(["AI Outfits", "My Outfits"])

    with tab_ai:
        if not ai_outfits:
            st.info("No outfits here yet. Go generate one!")
        else:
            st.caption(f"{len(ai_outfits)} outfit{'s' if len(ai_outfits) != 1 else ''}")
            _render_outfit_list(ai_outfits, tab_key="ai")

    with tab_manual:
        if not manual_outfits:
            st.info("No outfits here yet. Go create one!")
        else:
            st.caption(f"{len(manual_outfits)} outfit{'s' if len(manual_outfits) != 1 else ''}")
            _render_outfit_list(manual_outfits, tab_key="manual")


# ── Page 5 — Create Outfit ───────────────────────────────────────────────────

def page_create_outfit():
    st.title("Create Outfit")
    st.write("Select items from your wardrobe, then save them as an outfit.")

    try:
        resp = requests.get(f"{BASE_URL}/clothing/", headers=_headers(), timeout=8)
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot reach the API at {BASE_URL}.")
        return

    if not _check_auth(resp):
        return

    items = resp.json()

    if not items:
        st.info("Your wardrobe is empty. Add some items on the My Wardrobe page first!")
        return

    # Count currently selected items (read from widget state set by previous render)
    selected_ids = [item["id"] for item in items
                    if st.session_state.get(f"chk_create_{item['id']}", False)]
    st.caption(f"{len(selected_ids)} item{'s' if len(selected_ids) != 1 else ''} selected")

    # ── Selectable grid ──
    cols = st.columns(3)
    for i, item in enumerate(items):
        iid     = item["id"]
        chk_key = f"chk_create_{iid}"
        is_selected = st.session_state.get(chk_key, False)

        with cols[i % 3]:
            with st.container(border=True):
                # Green top bar highlights selected cards
                if is_selected:
                    st.markdown(
                        '<div style="background:#27ae60;height:3px;border-radius:3px;'
                        'margin-bottom:4px;"></div>',
                        unsafe_allow_html=True,
                    )

                st.checkbox("Select", key=chk_key, label_visibility="collapsed")

                # Image if available, else color swatch
                if item.get("image_url"):
                    try:
                        img_resp = requests.get(BASE_URL + item["image_url"], timeout=4)
                        if img_resp.status_code == 200:
                            st.image(img_resp.content, use_container_width=True)
                        else:
                            st.markdown(_color_swatch(item["color_code"]), unsafe_allow_html=True)
                    except requests.exceptions.RequestException:
                        st.markdown(_color_swatch(item["color_code"]), unsafe_allow_html=True)
                else:
                    st.markdown(_color_swatch(item["color_code"]), unsafe_allow_html=True)

                st.markdown(f"**{item['sub_category']}**")
                st.caption(item["category"])
                st.markdown(_color_swatch(item["color_code"]), unsafe_allow_html=True)

    st.divider()

    # ── Create form ──
    with st.form("create_outfit_form"):
        occasion    = st.selectbox("Occasion", OCCASIONS)
        outfit_name = st.text_input("Outfit name (optional)")
        create_btn  = st.form_submit_button("Create Outfit", type="primary")

    if create_btn:
        # Re-read selections at submit time
        selected_ids = [item["id"] for item in items
                        if st.session_state.get(f"chk_create_{item['id']}", False)]

        if len(selected_ids) < 2:
            st.error("Please select at least 2 items.")
        else:
            name = outfit_name.strip() or f"My Outfit - {datetime.today().strftime('%Y-%m-%d')}"
            post_resp = requests.post(
                f"{BASE_URL}/outfits/",
                json={
                    "name":               name,
                    "occasion":           occasion,
                    "clothing_item_ids":  selected_ids,
                },
                headers=_headers(),
                timeout=8,
            )
            if not _check_auth(post_resp):
                return
            if post_resp.status_code == 201:
                # Clear all checkbox states so the grid resets
                for item in items:
                    st.session_state.pop(f"chk_create_{item['id']}", None)
                st.success("Outfit created successfully!")
                st.rerun()
            else:
                detail = post_resp.json().get("detail", "Could not create outfit.")
                st.error(f"Error: {detail}")


# ── Main app shell ────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="SmartWardrobe AI",
        page_icon="👗",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialise session state
    if "token" not in st.session_state:
        st.session_state["token"] = None
    if "page" not in st.session_state:
        st.session_state["page"] = "Login"

    # If not logged in, always show Login
    if not st.session_state["token"] and st.session_state["page"] != "Login":
        st.session_state["page"] = "Login"

    # ── Sidebar navigation ──
    with st.sidebar:
        st.markdown("## 👗 SmartWardrobe AI")
        st.divider()

        if st.session_state["token"]:
            nav_pages = PAGES[1:]  # hide Login when logged in
            default_idx = (
                nav_pages.index(st.session_state["page"])
                if st.session_state["page"] in nav_pages
                else 0
            )
            selected = st.radio("Navigation", nav_pages, index=default_idx)
            st.session_state["page"] = selected

            st.divider()
            if st.button("Log out", use_container_width=True):
                st.session_state["token"] = None
                st.session_state["page"]  = "Login"
                st.rerun()
        else:
            st.info("Please log in to continue.")

    # ── Route to page ──
    page = st.session_state["page"]

    if page == "Login":
        page_login()
    elif page == "My Wardrobe":
        page_wardrobe()
    elif page == "Create Outfit":
        page_create_outfit()
    elif page == "Generate Outfit":
        page_generate()
    elif page == "My Outfits":
        page_outfits()


if __name__ == "__main__":
    main()
