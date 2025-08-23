# app/services/ai.py
import os
from typing import Optional
from dotenv import load_dotenv

import openai  # openai==1.x を想定（client.chat.completions.create を使用）

load_dotenv()


class AIService:
    """Service for OpenAI API interactions"""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # ★ 変更: 例外を投げずに無効化モードへ
            self.enabled = False
            self.client = None
            return

        # 通常動作
        self.enabled = True
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)

    def summarize_coach_comment(self, comment: str, max_length: int = 200) -> str:
        """Summarize coach comment using OpenAI GPT"""
        # ★ 追加: 無効化時はフォールバック
        if not getattr(self, "enabled", False):
            return comment[:max_length] + "..." if len(comment) > max_length else comment
        try:
            prompt = f"""
            以下のゴルフコーチングコメントを{max_length}文字以内で要約してください。
            重要なポイントや改善点を明確に含めてください。

            原文：
            {comment}

            要約：
            """
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは経験豊富なゴルフインストラクターです。コーチングコメントを簡潔に要約します。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=150,
                temperature=0.7,
            )
            summary = response.choices[0].message.content.strip()
            return summary if summary else comment[:max_length]
        except Exception as e:
            print(f"AI summarization failed: {e}")
            return comment[:max_length] + "..." if len(comment) > max_length else comment

    def analyze_swing_section(self, section_data: dict) -> str:
        """Analyze swing section data to suggest tags or improvements"""
        # ★ 追加: 無効化時は既定レスポンス
        if not getattr(self, "enabled", False):
            return {
                "suggested_tag": "other",
                "reasoning": "AI分析が無効化されています",
                "full_analysis": "",
            }
        try:
            start_sec = section_data.get("start_sec", 0)
            end_sec = section_data.get("end_sec", 0)
            coach_comment = section_data.get("coach_comment", "")

            prompt = f"""
            ゴルフスイングの以下のセクションを分析してください：

            時間範囲: {start_sec}秒 - {end_sec}秒
            コーチコメント: {coach_comment}

            以下の12のスイングフェーズから最も適切なタグを1つ選択してください：
            1. address (アドレス)
            2. takeaway (テイクバック)
            3. halfway_back (ハーフウェイバック)
            4. backswing (バックスイング)
            5. top (トップ)
            6. transition (切り返し)
            7. downswing (ダウンスイング)
            8. impact (インパクト)
            9. follow_through (フォロースイング)
            10. finish_1 (フィニッシュ-1)
            11. finish_2 (フィニッシュ-2)
            12. other (その他)

            回答形式：
            タグ: [選択したタグ]
            理由: [選択理由]
            """
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは経験豊富なゴルフインストラクターです。スイング分析の専門知識を持っています。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.3,
            )
            analysis = response.choices[0].message.content.strip()

            lines = analysis.split("\n")
            suggested_tag = "other"
            reasoning = ""
            for line in lines:
                if line.startswith("タグ:"):
                    tag_part = line.split(":", 1)[1].strip()
                    if "[" in tag_part and "]" in tag_part:
                        suggested_tag = tag_part.split("[", 1)[1].split("]", 1)[0]
                    else:
                        suggested_tag = tag_part.split()[0] if tag_part else "other"
                elif line.startswith("理由:"):
                    reasoning = line.split(":", 1)[1].strip()

            return {"suggested_tag": suggested_tag, "reasoning": reasoning, "full_analysis": analysis}
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return {"suggested_tag": "other", "reasoning": "AI分析が利用できませんでした", "full_analysis": ""}

    def summarize_overall_feedback(self, feedback: str, max_length: int = 300) -> str:
        """Summarize overall feedback about the golf swing"""
        # ★ 追加: 無効化時はフォールバック
        if not getattr(self, "enabled", False):
            return feedback[:max_length] + "..." if len(feedback) > max_length else feedback
        try:
            prompt = f"""
            以下のゴルフスイング全体に対するコーチの総評を{max_length}文字以内で要約してください。
            全体的な評価と主要な改善点を含めてください。

            原文：
            {feedback}

            要約：
            """
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは経験豊富なゴルフインストラクターです。スイング全体の総評を簡潔に要約します。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.7,
            )
            summary = response.choices[0].message.content.strip()
            return summary if summary else feedback[:max_length]
        except Exception as e:
            print(f"AI overall feedback summarization failed: {e}")
            return feedback[:max_length] + "..." if len(feedback) > max_length else feedback

    def summarize_training_menu(self, training_menu: str, max_length: int = 300) -> str:
        """Summarize next training menu suggestions"""
        # ★ 追加: 無効化時はフォールバック
        if not getattr(self, "enabled", False):
            return training_menu[:max_length] + "..." if len(training_menu) > max_length else training_menu
        try:
            prompt = f"""
            以下のゴルフ練習メニュー提案を{max_length}文字以内で要約してください。
            具体的な練習内容と目的を含めてください。

            原文：
            {training_menu}

            要約：
            """
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは経験豊富なゴルフインストラクターです。練習メニューを簡潔に要約します。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.7,
            )
            summary = response.choices[0].message.content.strip()
            return summary if summary else training_menu[:max_length]
        except Exception as e:
            print(f"AI training menu summarization failed: {e}")
            return training_menu[:max_length] + "..." if len(training_menu) > max_length else training_menu


# Global AI service instance
ai_service = AIService()
