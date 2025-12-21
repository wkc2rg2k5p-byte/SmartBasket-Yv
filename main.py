#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""家庭协作式智能菜篮 0.0.1"""

from core import ai_suggest, save_ingredients

def cli_menu():
    print("=== SmartBasket ===")
    dish = input("请输入今日想吃的菜：")
    people = input("几人份？：")
    # 假装调用 AI
    recipes = ai_suggest(dish, people)
    print("\n🤖返回菜谱：")
    for r in recipes:
        print(" -", r)

    confirm = input("\n生成食材清单吗？(y/n)：")
    if confirm.lower() == 'y':
        save_ingredients(recipes)
        print("✅ 食材清单已导出到 basket.txt")

if __name__ == '__main__':
    cli_menu()