import pandas as pd
import re

def clean_key(val):
    """标准化清洗：转字符串 + 移除所有空白字符"""
    if pd.isna(val):
        return None
    s = str(val)
    s = re.sub(r'\s+', '', s)
    return s if s != '' else None


# ======================
# 公共函数：构建图结构（仅用于 mode=4）
# ======================
def build_graph_from_main_df(df):
    forward_map = {}      # A_clean -> [B_clean]
    reverse_map = {}      # B_clean -> [A_clean]
    a_to_c = {}           # A_clean -> set(C)

    for _, row in df.iterrows():
        a_clean = clean_key(row[0])  # A 列
        b_clean = clean_key(row[1])  # B 列
        c_val = row[2]

        if a_clean is not None and b_clean is not None:
            if a_clean not in forward_map:
                forward_map[a_clean] = []
            forward_map[a_clean].append(b_clean)

            if b_clean not in reverse_map:
                reverse_map[b_clean] = []
            reverse_map[b_clean].append(a_clean)

        if a_clean is not None and pd.notna(c_val):
            if a_clean not in a_to_c:
                a_to_c[a_clean] = set()
            a_to_c[a_clean].add(c_val)

    return forward_map, reverse_map, a_to_c


# ======================
# 公共函数：从 C 值提取关键词并匹配 COLOR
# ======================
def extract_and_match_color(all_c_values, color_sheet_path="E4C_all_trans_AI.xlsx"):
    extracted_keywords = set()
    for c_val in all_c_values:
        if isinstance(c_val, str):
            matches = re.findall(r'"([^"]*)"', c_val)
            for m in matches:
                if m != '':
                    extracted_keywords.add(m)

    # 加载 COLOR 表
    color_results = set()
    try:
        df_color = pd.read_excel(color_sheet_path, sheet_name="COLOR")
        if 'NAME' not in df_color.columns or 'COLOR' not in df_color.columns:
            pass  # 无有效列，跳过
        else:
            name_to_colors = {}
            for _, row in df_color.iterrows():
                name_raw = row['NAME']
                color_raw = row['COLOR']
                if pd.notna(name_raw) and pd.notna(color_raw):
                    name_str = str(name_raw)  # 保持原始，不 strip
                    color_str = str(color_raw).strip()
                    if color_str:
                        if name_str not in name_to_colors:
                            name_to_colors[name_str] = set()
                        name_to_colors[name_str].add(color_str)

            for kw in extracted_keywords:
                if kw in name_to_colors:
                    color_results.update(name_to_colors[kw])

    except (ValueError, FileNotFoundError):
        pass  # 无 COLOR 表或文件缺失，color_results 为空

    return sorted(color_results)


# ======================
# 原有追溯函数（用于 mode 1/2/3）
# ======================
def _run_forward_trace(main_df, start_str, visited_indices, output_c_list, collected_a, collected_b):
    b_to_rows = _build_mapping(main_df, key_col=1)
    current_keys = [start_str]
    while current_keys:
        next_keys = []
        for key in current_keys:
            if key in b_to_rows:
                for match in b_to_rows[key]:
                    idx = match['index']
                    if idx not in visited_indices:
                        visited_indices.add(idx)
                        output_c_list.append(match['c_value'])
                        collected_a.append(match['a_value'])
                        collected_b.append(match['b_value'])
                        next_keys.append(match['a_value'])
        current_keys = next_keys


def _run_upward_trace(main_df, start_str, visited_indices, output_c_list, collected_a, collected_b):
    a_to_rows = _build_mapping(main_df, key_col=0)
    current_keys = [start_str]
    while current_keys:
        next_keys = []
        for key in current_keys:
            if key in a_to_rows:
                for match in a_to_rows[key]:
                    idx = match['index']
                    if idx not in visited_indices:
                        visited_indices.add(idx)
                        output_c_list.append(match['c_value'])
                        collected_a.append(match['a_value'])
                        collected_b.append(match['b_value'])
                        next_keys.append(match['b_value'])
        current_keys = next_keys


def _build_mapping(df, key_col):
    mapping = {}
    for idx, row in df.iterrows():
        key = str(row[key_col]).strip()
        if key not in mapping:
            mapping[key] = []
        mapping[key].append({
            'a_value': str(row[0]).strip(),
            'b_value': str(row[1]).strip(),
            'c_value': str(row[2]).strip(),
            'index': idx
        })
    return mapping


# ======================
# 主程序
# ======================
def main():
    # 读取主工作表
    try:
        main_df = pd.read_excel(
            "E4C_all_trans_AI.xlsx",
            sheet_name=0,
            header=None,
            usecols=[0, 1, 2]
        )
    except FileNotFoundError:
        print("❌ 文件 'E4C_all_trans_AI.xlsx' 未找到！")
        return
    except Exception as e:
        print(f"❌ 读取主工作表时出错：{e}")
        return

    main_df = main_df.dropna(subset=[0, 1, 2]).reset_index(drop=True)

    # 输入起始位置
    start_str = input("请输入开始位置: ").strip()
    if not start_str:
        print("⚠️ 输入为空，程序退出。")
        return

    # 选择模式
    print("请选择追溯模式：")
    print("1. 向下追溯：从当前对象向数据源方向展开")
    print("2. 向上追溯：从当前对象向数据上游展开")
    print("3. 向上+向下：数据流1+数据流2")
    print("4. 全量数据流：向上+向下+所有节点关联的数据流")
    choice = input("请输入 1、2、3 或 4: ").strip()

    if choice not in ("1", "2", "3", "4"):
        print("⚠️ 无效输入，程序退出。")
        return

    # =============== 模式 4：全量数据流（新逻辑）===============
    if choice == "4":
        start_clean = clean_key(start_str)
        if start_clean is None:
            print("⚠️ 起始关键词无效，退出。")
            return

        forward_map, reverse_map, a_to_c = build_graph_from_main_df(main_df)

        # 正向传播（A → B）
        visited_forward = set()
        queue = [start_clean]
        while queue:
            cur = queue.pop(0)
            if cur in visited_forward:
                continue
            visited_forward.add(cur)
            if cur in forward_map:
                for nxt in forward_map[cur]:
                    if nxt not in visited_forward:
                        queue.append(nxt)

        # 反向传播（B ← A）
        visited_backward = set()
        queue = [start_clean]
        while queue:
            cur = queue.pop(0)
            if cur in visited_backward:
                continue
            visited_backward.add(cur)
            if cur in reverse_map:
                for src in reverse_map[cur]:
                    if src not in visited_backward:
                        queue.append(src)

        # 合并所有节点
        all_nodes = visited_forward | visited_backward

        # 收集 C 值
        all_c_values = set()
        for node in all_nodes:
            if node in a_to_c:
                all_c_values.update(a_to_c[node])
        all_c_values = sorted(all_c_values)

        # 输出 C
        if all_c_values:
            print("\n## ✅ 全量数据流结果（C列内容）:")
            for c in all_c_values:
                print(c)
        else:
            print("\n🔍 未找到任何 C 值。")

        # COLOR 匹配
        color_results = extract_and_match_color(all_c_values)
        if color_results:
            print("\n## 🎨 COLOR 匹配结果（仅 COLOR 列）:")
            for col in color_results:
                print(col)
        else:
            print("\n🎨 在 COLOR 工作表中未找到匹配的 COLOR 值。")

        return  # mode=4 结束

    # =============== 模式 1/2/3：原有行级追溯逻辑 ===============
    output_c_list = []
    collected_a_values = []
    collected_b_values = []

    if choice == "1":
        visited = set()
        _run_forward_trace(main_df, start_str, visited, output_c_list, collected_a_values, collected_b_values)
    elif choice == "2":
        visited = set()
        _run_upward_trace(main_df, start_str, visited, output_c_list, collected_a_values, collected_b_values)
    elif choice == "3":
        visited = set()
        _run_forward_trace(main_df, start_str, visited, output_c_list, collected_a_values, collected_b_values)
        _run_upward_trace(main_df, start_str, visited, output_c_list, collected_a_values, collected_b_values)

    # 输出 C
    if output_c_list:
        mode_name = {"1": "向下追溯", "2": "向上追溯", "3": "向上+向下"}[choice]
        print(f"\n## ✅ {mode_name}结果（C列内容）:")
        for c in output_c_list:
            print(c)
    else:
        print("\n🔍 未找到任何匹配的行。")

    # COLOR 查询（旧逻辑，基于 collected A/B）
    try:
        color_df = pd.read_excel("E4C_all_trans_AI.xlsx", sheet_name="COLOR", header=None, usecols=[0, 1])
        color_df = color_df.dropna(subset=[0, 1]).reset_index(drop=True)
        name_to_colors = {}
        for _, row in color_df.iterrows():
            name = str(row[0]).strip()
            color_val = str(row[1]).strip()
            name_to_colors.setdefault(name, []).append(color_val)

        seen_names = set()
        query_names_in_order = []
        for name in collected_a_values + collected_b_values:
            if name not in seen_names:
                seen_names.add(name)
                query_names_in_order.append(name)

        color_output_list = []
        seen_colors = set()
        for name in query_names_in_order:
            if name in name_to_colors:
                for color in name_to_colors[name]:
                    if color not in seen_colors:
                        seen_colors.add(color)
                        color_output_list.append(color)

        if color_output_list:
            print("\n## 🎨 COLOR 匹配结果（仅 COLOR 列）:")
            for color in color_output_list:
                print(color)
        else:
            print("\n🎨 在 COLOR 工作表中未找到匹配的 COLOR 值。")

    except Exception:
        print("\n⚠️ COLOR 表加载失败，跳过 COLOR 查询。")


if __name__ == "__main__":
    main()
