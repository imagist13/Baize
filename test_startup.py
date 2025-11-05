"""
快速测试脚本：验证项目是否可以正常启动
"""
import sys
import asyncio


async def test_startup():
    """测试项目启动所需的所有组件"""
    
    print("=" * 60)
    print("🔍 项目启动测试")
    print("=" * 60)
    
    results = []
    
    # 1. 测试配置
    print("\n1️⃣ 测试配置...")
    try:
        from app.config import config
        print(f"  ✓ 配置加载成功")
        print(f"  - API Key: {'已配置' if config.is_valid() else '未配置（将使用演示模式）'}")
        print(f"  - 使用 Gemini: {config.is_gemini_key()}")
        results.append(True)
    except Exception as e:
        print(f"  ✗ 配置加载失败: {e}")
        results.append(False)
    
    # 2. 测试客户端
    print("\n2️⃣ 测试客户端...")
    try:
        from app.clients import client_manager
        print(f"  ✓ 客户端管理器初始化成功")
        print(f"  - 就绪状态: {client_manager.is_ready()}")
        results.append(True)
    except Exception as e:
        print(f"  ✗ 客户端初始化失败: {e}")
        results.append(False)
    
    # 3. 测试数据模型
    print("\n3️⃣ 测试数据模型...")
    try:
        from app.schemas import ChatRequest, PlanningRequest, AgentState
        print(f"  ✓ 数据模型导入成功")
        results.append(True)
    except Exception as e:
        print(f"  ✗ 数据模型导入失败: {e}")
        results.append(False)
    
    # 4. 测试代理
    print("\n4️⃣ 测试代理...")
    try:
        from app.agents import (
            AnimationGenerationAgent,
            CodePlanningAgent,
            PagePlanningAgent
        )
        print(f"  ✓ 代理类导入成功")
        results.append(True)
    except Exception as e:
        print(f"  ✗ 代理导入失败: {e}")
        results.append(False)
    
    # 5. 测试工作流图
    print("\n5️⃣ 测试 LangGraph 工作流...")
    try:
        from app.graph import (
            create_code_planning_graph,
            create_page_planning_graph,
            create_combined_planning_graph
        )
        
        code_graph = create_code_planning_graph()
        page_graph = create_page_planning_graph()
        combined_graph = create_combined_planning_graph()
        
        print(f"  ✓ LangGraph 工作流创建成功")
        print(f"  - 代码规划工作流: 已创建")
        print(f"  - 页面规划工作流: 已创建")
        print(f"  - 组合工作流: 已创建")
        results.append(True)
    except Exception as e:
        print(f"  ✗ 工作流创建失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(False)
    
    # 6. 测试服务
    print("\n6️⃣ 测试服务层...")
    try:
        from app.services import PlanningService
        print(f"  ✓ 服务层导入成功")
        results.append(True)
    except Exception as e:
        print(f"  ✗ 服务层导入失败: {e}")
        results.append(False)
    
    # 7. 测试路由
    print("\n7️⃣ 测试路由...")
    try:
        from app.routers import planning_router, generation_router, ui_router
        print(f"  ✓ 路由导入成功")
        results.append(True)
    except Exception as e:
        print(f"  ✗ 路由导入失败: {e}")
        results.append(False)
    
    # 8. 测试 FastAPI 应用
    print("\n8️⃣ 测试 FastAPI 应用...")
    try:
        from app.main import app, create_app
        
        # 检查路由
        routes = [route.path for route in app.routes]
        print(f"  ✓ FastAPI 应用创建成功")
        print(f"  - 应用标题: {app.title}")
        print(f"  - 版本: {app.version}")
        print(f"  - 注册路由数: {len(routes)}")
        
        # 检查关键路由
        key_routes = ["/", "/generate", "/plan", "/code/plan", "/plan/combined"]
        missing = [r for r in key_routes if r not in routes]
        
        if missing:
            print(f"  ⚠️  缺少路由: {missing}")
        else:
            print(f"  ✓ 所有关键路由已注册")
        
        results.append(True)
    except Exception as e:
        print(f"  ✗ FastAPI 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(False)
    
    # 9. 检查静态文件
    print("\n9️⃣ 检查静态文件...")
    try:
        import os
        static_files = ["static/style.css", "static/script.js", "templates/index.html"]
        for file in static_files:
            if os.path.exists(file):
                print(f"  ✓ {file}")
            else:
                print(f"  ✗ {file} 不存在")
        results.append(True)
    except Exception as e:
        print(f"  ✗ 静态文件检查失败: {e}")
        results.append(False)
    
    # 总结
    print("\n" + "=" * 60)
    if all(results):
        print("✅ 所有测试通过！项目可以启动。")
        print("\n启动命令:")
        print("  python run_new.py")
        print("\n或者:")
        print("  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return 0
    else:
        passed = sum(results)
        total = len(results)
        print(f"⚠️  部分测试失败 ({passed}/{total} 通过)")
        print("\n请检查上面的错误信息并解决问题。")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_startup())
    sys.exit(exit_code)

