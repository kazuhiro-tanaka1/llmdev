# graph.py
from typing import TypedDict, Optional
import os
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from tavily import TavilyClient

from langgraph.graph import StateGraph

# 環境変数を読み込む
load_dotenv(".env")
os.environ['OPENAI_API_KEY'] = os.environ['API_KEY']

# State定義
class State(TypedDict):
    query: str
    route: Optional[str]
    context: Optional[str]
    answer: Optional[str]

# 初期化
llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0
)

embedding = OpenAIEmbeddings()
vectordb = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding
)
retriever = vectordb.as_retriever()

tavily = TavilyClient()

# ノード定義
# ルーター
def router_node(state: State) -> State:
    query = state["query"]

    routing_prompt = f"""
あなたは優秀なAIルーターです。
以下の質問を「web」「rag」「llm」のいずれかに分類してください。

分類基準：
- web: 最新情報・ニュース・リアルタイム・外部情報が必要
- rag: 社内データ・独自ドキュメント・ローカルDB参照
- llm: 一般知識・雑談・説明・推論

さらに「確信度（0.0〜1.0）」も出してください。

出力形式：
route: <web|rag|llm>
confidence: <0.0〜1.0>

例：
route: web
confidence: 0.92

---

質問:
{query}
"""

    try:
        result = llm.predict(routing_prompt)

        # パース処理
        lines = result.strip().lower().split("\n")
        route = "llm"
        confidence = 0.5

        for line in lines:
            if "route:" in line:
                route = line.split("route:")[1].strip()
            if "confidence:" in line:
                confidence = float(line.split("confidence:")[1].strip())

        # バリデーション
        if route not in ["web", "rag", "llm"]:
            route = "llm"

        if confidence < 0.6:
            route = "llm"

    except Exception:
        # 完全フォールバック
        route = "llm"
        confidence = 0.0

    # デバッグ用（おすすめ）
    print(f"[ROUTER] query={query} route={route} confidence={confidence}")

    state["route"] = route
    return state


# Web検索
def web_node(state: State) -> State:
    result = tavily.search(query=state["query"])
    state["context"] = str(result["results"])
    return state


# RAG検索
def rag_node(state: State) -> State:
    docs = retriever.get_relevant_documents(state["query"])

    if docs:
        state["context"] = "\n".join([d.page_content for d in docs])
    else:
        state["context"] = "関連情報は見つかりませんでした。"

    return state


# LLM生成
def llm_node(state: State) -> State:
    query = state["query"]
    context = state.get("context", "")

    prompt = f"""
あなたは優秀なAIアシスタントです。

以下の参考情報があれば活用してください：
{context}

ユーザーの質問：
{query}
"""

    response = llm.predict(prompt)

    state["answer"] = response
    return state


# グラフ構築
builder = StateGraph(State)

builder.add_node("router", router_node)
builder.add_node("web", web_node)
builder.add_node("rag", rag_node)
builder.add_node("llm", llm_node)

# エントリーポイント
builder.set_entry_point("router")

# 分岐
builder.add_conditional_edges(
    "router",
    lambda state: state["route"],
    {
        "web": "web",
        "rag": "rag",
        "llm": "llm"
    }
)

# フロー
builder.add_edge("web", "llm")
builder.add_edge("rag", "llm")

# コンパイル
graph = builder.compile()

# 実行関数
def run_chat(query: str) -> str:
    result = graph.invoke({
        "query": query,
        "route": None,
        "context": None,
        "answer": None
    })

    return result["answer"]