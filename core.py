# -*- coding: utf-8 -*-

def ai_suggest(keyword: str, people: str):
    """
    接入通义千问 API 
    """
    # TODO: 调用通义千问 API / 本地大模型
    return [
        f"{keyword}风味家常菜（{people}人份）",
        "清炒时蔬"
    ]

def save_ingredients(recipes):
    """把食材写进txt"""
    # TODO: 真正合并同类项、计算克重
    with open("basket.txt", "w", encoding="utf-8") as f:
        f.write("SmartBasket 食材清单\n======================\n")
        for r in recipes:
            f.write(f"- {r} 所需食材：***暂缺***\n")
        f.write("\n采购员可在终端勾选已买/缺货——功能待写\n")